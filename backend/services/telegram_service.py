import asyncio
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config.system_config import JarvisConfig
from services.voice_speaker import VoiceSpeaker
import os

logger = logging.getLogger("TelegramService")

class TelegramService:
    def __init__(self, orchestrator=None):
        self.token = JarvisConfig.TELEGRAM_TOKEN
        self.authorized_chat_id = JarvisConfig.AUTHORIZED_CHAT_ID
        self.orchestrator = orchestrator
        self.application = None
        self.voice_speaker = VoiceSpeaker()
        self.auth_response_event = asyncio.Event()
        self.last_auth_result = None
        
        try:
            from core.llm_router import HybridModelRouter
            self.router = HybridModelRouter()
            logger.info("HybridModelRouter initialized in TelegramService.")
        except Exception as e:
            logger.error(f"Failed to initialize router: {e}")
            self.router = None
            
        try:
            from core.vision_router import VisionRouter
            self.vision_router = VisionRouter()
            logger.info("VisionRouter initialized in TelegramService.")
        except Exception as e:
            logger.error(f"Failed to initialize vision router: {e}")
            self.vision_router = None
            
        try:
            from core.agent_matrix import AgentMatrix
            self.agent_matrix = AgentMatrix()
            logger.info("AgentMatrix initialized in TelegramService.")
        except Exception as e:
            logger.error(f"Failed to initialize AgentMatrix: {e}")
            self.agent_matrix = None
            
        try:
            from core.data_synthesizer import DataSynthesizer
            self.data_synthesizer = DataSynthesizer()
            logger.info("DataSynthesizer initialized in TelegramService.")
        except Exception as e:
            logger.error(f"Failed to initialize DataSynthesizer: {e}")
            self.data_synthesizer = None

    async def start(self):
        """Starts the Telegram bot polling in the background."""
        if not self.token or self.token == "we_will_add_this_later":
            logger.warning("Telegram Bot Token is missing. Bot will not start.")
            return

        try:
            self.application = ApplicationBuilder().token(self.token).build()

            # Command Handlers
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("approve", self._approve_command))
            self.application.add_handler(CommandHandler("deny", self._deny_command))
            
            # Message Handler (Chat with JARVIS)
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))
            
            # Document & Media Handlers (For Knowledge Ingestion)
            self.application.add_handler(MessageHandler(filters.Document.ALL, self._handle_document))
            self.application.add_handler(MessageHandler(filters.PHOTO, self._handle_photo))
            
            # Button Callback Handler
            self.application.add_handler(CallbackQueryHandler(self._button_callback))

            # Global Error Handler
            self.application.add_error_handler(self._error_handler)

            logger.info("Telegram Bot is starting...")
            await self.application.initialize()
            await self.application.start()

            # ── CONFLICT EVICTION ──────────────────────────────────────────
            # Loop until Telegram confirms slot is OURS (200 OK).
            # A ghost can hold the slot for up to 30 seconds after process kill.
            logger.info("[Telegram] Evicting any ghost polling sessions...")
            import httpx
            evicted = False
            for attempt in range(30):  # max 30s wait
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        resp = await client.post(
                            f"https://api.telegram.org/bot{self.token}/getUpdates",
                            json={"timeout": 0, "limit": 1}
                        )
                    if resp.status_code == 200:
                        logger.info(f"[Telegram] Slot claimed successfully (attempt {attempt+1}).")
                        evicted = True
                        await asyncio.sleep(1)  # Let server propagate
                        break
                    else:
                        logger.debug(f"[Telegram] Eviction attempt {attempt+1}: HTTP {resp.status_code}. Retrying...")
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.debug(f"[Telegram] Eviction attempt {attempt+1} error: {e}. Retrying...")
                    await asyncio.sleep(1)
            if not evicted:
                logger.warning("[Telegram] Could not confirm slot eviction. Proceeding anyway.")
            # ─────────────────────────────────────────────────────────────

            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            logger.info("Telegram Bot is online.")
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot: {e}")


    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        from telegram.error import Conflict, NetworkError
        # Swallow transient network/conflict errors — they self-resolve
        if isinstance(context.error, (Conflict, NetworkError)):
            logger.warning(f"[Telegram] Transient error (will retry): {context.error}")
        else:
            logger.error(f"Telegram Exception: {context.error}")


    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        
        # Always show ID to help with setup
        await update.message.reply_text(f"Hello! Your Telegram Chat ID is: {chat_id}")
        
        if self.authorized_chat_id and self.authorized_chat_id != "your_id_here":
            if chat_id != str(self.authorized_chat_id):
                await update.message.reply_text("⛔ Access Denied. This ID is not in the authorized whitelist.")
                logger.warning(f"Unauthorized access attempt from Chat ID: {chat_id}")
                return
            else:
                await update.message.reply_text("✅ Identity Verified. I am standing by for your commands, Boss.")
        else:
            await update.message.reply_text("⚠️ Security Note: No authorized Chat ID is set in .env yet. Please provide this ID to the developer.")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        if self.authorized_chat_id and chat_id != str(self.authorized_chat_id):
            return

        user_input = update.message.text
        logger.info(f"Telegram Message from {chat_id}: {user_input}")

        if self.router and user_input.startswith("!route "):
            prompt = user_input[7:]
            task_type = "chat"
            if "code" in prompt.lower() or "python" in prompt.lower() or len(prompt) > 50:
                task_type = "complex_coding"
            
            await update.message.reply_text(f"🚀 [Router] Processing via {task_type} route...")
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, self.router.route_prompt, task_type, prompt)
                await update.message.reply_text(f"🤖 {response}")
                return
            except Exception as e:
                logger.error(f"Router failed: {e}")
                await update.message.reply_text(f"⚠️ Router Error: {e}")
                
        if getattr(self, 'agent_matrix', None) and user_input.startswith("!simulate "):
            problem = user_input[10:]
            
            async def progress_callback_async(msg):
                try:
                    await update.message.reply_text(msg, parse_mode='Markdown')
                except:
                    pass

            def sync_callback(msg):
                asyncio.run_coroutine_threadsafe(progress_callback_async(msg), asyncio.get_running_loop())
                
            await update.message.reply_text("🌀 **Entering The Agent Matrix**...\n*Initializing Simulation...*", parse_mode='Markdown')
            try:
                from functools import partial
                loop = asyncio.get_running_loop()
                simulate_call = partial(self.agent_matrix.simulate, problem, progress_callback=sync_callback)
                final_answer = await loop.run_in_executor(None, simulate_call)
                await update.message.reply_text(f"🏆 **Final Verified Answer:**\n\n{final_answer}", parse_mode='Markdown')
                return
            except Exception as e:
                logger.error(f"Matrix failed: {e}")
                await update.message.reply_text(f"⚠️ Matrix Simulation Error: {e}")
                return

        if getattr(self, 'data_synthesizer', None) and user_input.startswith("!synthesize "):
            topic = user_input[12:]
            
            async def progress_callback_async_synth(msg):
                try:
                    await update.message.reply_text(msg, parse_mode='Markdown')
                except:
                    pass

            def sync_callback_synth(msg):
                asyncio.run_coroutine_threadsafe(progress_callback_async_synth(msg), asyncio.get_running_loop())
                
            await update.message.reply_text(f"📚 **Entering Teacher-Student Pipeline**...\n*Preparing to generate data on: {topic}*", parse_mode='Markdown')
            try:
                from functools import partial
                loop = asyncio.get_running_loop()
                synth_call = partial(self.data_synthesizer.generate_data, topic, 3, progress_callback=sync_callback_synth)
                result = await loop.run_in_executor(None, synth_call)
                await update.message.reply_text(f"🎉 **Study Session Complete!**\n\n{result}", parse_mode='Markdown')
                return
            except Exception as e:
                logger.error(f"Synthesizer failed: {e}")
                await update.message.reply_text(f"⚠️ Synthesis Error: {e}")
                return

        if self.orchestrator:
            # Route to orchestrator via process_telegram_command
            response = await self.orchestrator.process_telegram_command(user_input, sender=chat_id)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("I am connected, but my brain (Orchestrator) is not initialized properly.")

    async def _handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processes incoming files/PDFs for knowledge ingestion."""
        chat_id = str(update.effective_chat.id)
        if self.authorized_chat_id and chat_id != str(self.authorized_chat_id):
            return

        doc = update.message.document
        file_name = doc.file_name
        logger.info(f"Receiving document from {chat_id}: {file_name}")

        try:
            # Download file
            new_file = await context.bot.get_file(doc.file_id)
            os.makedirs("data/ingestion", exist_ok=True)
            file_path = f"data/ingestion/{file_name}"
            await new_file.download_to_drive(file_path)

            extracted_text = ""
            ext = file_name.lower().split('.')[-1]
            
            if ext == "pdf":
                extracted_text = self._extract_pdf_text(file_path)
            elif ext == "docx":
                extracted_text = self._extract_docx_text(file_path)
            elif ext in ["xlsx", "xls"]:
                extracted_text = self._extract_excel_text(file_path)
            elif ext == "csv":
                extracted_text = self._extract_csv_text(file_path)
            elif ext in ["txt", "md", "json"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    extracted_text = f.read()

            if extracted_text and len(extracted_text.strip()) > 10:
                if self.orchestrator:
                    # Feed to brain
                    await update.message.reply_text(f"📥 Processing and summarizing `{file_name}`...")
                    
                    # Create a specific learning prompt that requests a summary
                    learn_msg = (
                        f"I have received a document named '{file_name}'. "
                        f"Please learn the following content and provide a concise 3-5 bullet point summary "
                        f"of the key information for the owner:\n\n{extracted_text[:4000]}"
                    )
                    
                    summary = await self.orchestrator.process_telegram_command(learn_msg, sender=chat_id)
                    
                    # Write to Obsidian Knowledge Vault
                    self._write_book_to_vault(file_name, summary, extracted_text)
                    
                    await update.message.reply_text(
                        f"✅ *Knowledge Integrated*\n\n"
                        f"*Summary of {file_name}:*\n{summary}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text("I've saved the file, but I can't process it without an orchestrator.")
            else:
                await update.message.reply_text("File received, but I couldn't extract any readable text from it.")

        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            await update.message.reply_text(f"⚠️ Error processing document: {str(e)}")

    async def _handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processes incoming photos for OCR ingestion."""
        chat_id = str(update.effective_chat.id)
        if self.authorized_chat_id and chat_id != str(self.authorized_chat_id):
            return

        photo = update.message.photo[-1] # Highest resolution
        logger.info(f"Receiving photo from {chat_id}")

        try:
            new_file = await context.bot.get_file(photo.file_id)
            os.makedirs("data/ingestion", exist_ok=True)
            import time
            file_path = f"data/ingestion/photo_{int(time.time())}.jpg"
            await new_file.download_to_drive(file_path)

            await update.message.reply_text("📸 Image received. I am looking at it now...")
            
            if hasattr(self, 'vision_router') and self.vision_router:
                try:
                    loop = asyncio.get_running_loop()
                    # Ask the user's caption if any, otherwise default prompt
                    prompt = update.message.caption if update.message.caption else "Describe this image in detail. Identify any objects, read any visible text, and explain the context."
                    
                    analysis = await loop.run_in_executor(
                        None, 
                        self.vision_router.analyze_image, 
                        file_path,
                        prompt
                    )
                    await update.message.reply_text(f"👁️ **Vision Analysis:**\n\n{analysis}", parse_mode='Markdown')
                except Exception as ve:
                    logger.error(f"Vision router failed: {ve}")
                    await update.message.reply_text("⚠️ Vision processing failed.")
            else:
                await update.message.reply_text("My Vision system is currently offline.")
            
        except Exception as e:
            logger.error(f"Failed to process photo: {e}")

    def _extract_pdf_text(self, path: str) -> str:
        """Helper to extract text from PDF using PyPDF2."""
        try:
            import PyPDF2
            text = ""
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF Extraction error: {e}")
            return ""

    def _extract_docx_text(self, path: str) -> str:
        """Helper to extract text from Word documents."""
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"DOCX Extraction error: {e}")
            return ""

    def _extract_excel_text(self, path: str) -> str:
        """Helper to extract text from Excel spreadsheets."""
        try:
            import pandas as pd
            df = pd.read_excel(path)
            return df.to_string()
        except Exception as e:
            logger.error(f"Excel Extraction error: {e}")
            return ""

    def _extract_csv_text(self, path: str) -> str:
        """Helper to extract text from CSV files."""
        try:
            import pandas as pd
            df = pd.read_csv(path)
            return df.to_string()
        except Exception as e:
            logger.error(f"CSV Extraction error: {e}")
            return ""

    def _write_book_to_vault(self, file_name: str, summary: str, full_text: str):
        """Write a book entry to the Obsidian Knowledge Vault and update Books_Overview."""
        try:
            from pathlib import Path
            from datetime import datetime
            
            vault_books = Path("JARVIS-v2/arion/vault/Knowledge/Books")
            vault_books.mkdir(parents=True, exist_ok=True)
            
            # Clean book title from filename
            book_title = file_name.rsplit('.', 1)[0]  # Remove extension
            book_title = book_title.replace('_', ' ').replace('  ', ' ').strip()
            # Create safe filename
            safe_name = book_title.replace(' ', '_').replace('(', '').replace(')', '')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # 1. Create individual book note
            book_note = vault_books / f"{safe_name}.md"
            book_content = (
                f"---\n"
                f"type: book\n"
                f"title: \"{book_title}\"\n"
                f"ingested: {date_str}\n"
                f"source: telegram_upload\n"
                f"---\n\n"
                f"# {book_title}\n\n"
                f"## Summary\n{summary}\n\n"
                f"## Key Excerpt\n{full_text[:2000]}\n\n"
                f"---\n"
                f"[[Knowledge/Books/Books_Overview]]\n"
            )
            book_note.write_text(book_content, encoding='utf-8')
            logger.info(f"Vault: Created book note {book_note.name}")
            
            # 2. Update Books_Overview
            overview_path = vault_books / "Books_Overview.md"
            if overview_path.exists():
                content = overview_path.read_text(encoding='utf-8')
                
                # Count existing books by counting [[Knowledge/Books/ links
                import re
                existing_links = re.findall(r'\[\[Knowledge/Books/', content)
                # Don't count the self-reference to Books_Overview
                book_count = len([l for l in existing_links if 'Books_Overview' not in l])
                new_count = book_count + 1
                
                # Update total_books in frontmatter
                content = re.sub(r'total_books: \d+', f'total_books: {new_count}', content)
                content = re.sub(r'last_updated: .+', f'last_updated: {date_str}', content)
                
                # Replace the placeholder or append to the book list
                book_link = f"- [[Knowledge/Books/{safe_name}|{book_title}]] *(ingested {date_str})*"
                
                if '*Nothing yet. Feed me books.*' in content:
                    content = content.replace('*Nothing yet. Feed me books.*', book_link)
                elif '## Books ARION Has Read' in content:
                    # Append after existing entries
                    content = content.replace(
                        '## Books ARION Has Read\n',
                        f'## Books ARION Has Read\n{book_link}\n'
                    )
                
                overview_path.write_text(content, encoding='utf-8')
                logger.info(f"Vault: Updated Books_Overview (total: {new_count})")
            
        except Exception as e:
            logger.error(f"Failed to write book to vault: {e}")


    async def _approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Placeholder for permission logic
        await update.message.reply_text("Permission Approved.")

    async def _deny_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Placeholder for permission logic
        await update.message.reply_text("Permission Denied.")

    async def request_authorization(self, photo_path: str):
        """Sends a photo to the user with Approve/Deny buttons and waits for response."""
        if not self.application or not self.authorized_chat_id:
            logger.error("Telegram Service not fully initialized. Cannot request auth.")
            return False

        self.auth_response_event.clear()
        self.last_auth_result = None

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data='auth_approve'),
                InlineKeyboardButton("❌ Deny", callback_data='auth_deny'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            with open(photo_path, 'rb') as photo:
                await self.application.bot.send_photo(
                    chat_id=self.authorized_chat_id,
                    photo=photo,
                    caption="🛡️ SECURITY ALERT: Unrecognized face detected. Do you authorize access?",
                    reply_markup=reply_markup
                )
            
            # Wait for user input (60 second timeout)
            try:
                await asyncio.wait_for(self.auth_response_event.wait(), timeout=60.0)
                return self.last_auth_result
            except asyncio.TimeoutError:
                logger.warning("Authorization request timed out.")
                await self.application.bot.send_message(
                    chat_id=self.authorized_chat_id,
                    text="⏳ Authorization request timed out. Access denied automatically."
                )
                return False

        except Exception as e:
            logger.error(f"Error in request_authorization: {e}")
            return False

    async def request_user_authorization(self, sender_id: str, message_text: str):
        """
        Sends a text message with Approve/Deny buttons for a new user.
        Retries every 5 minutes for 1 hour until response.
        """
        if not self.application or not self.authorized_chat_id:
            logger.error("Telegram Service not fully initialized. Cannot request auth.")
            return False

        max_attempts = 12  # 12 * 5 min = 60 min
        retry_interval = 300 # 5 minutes

        for attempt in range(1, max_attempts + 1):
            self.auth_response_event.clear()
            self.last_auth_result = None

            keyboard = [
                [
                    InlineKeyboardButton("✅ Allow", callback_data=f'user_allow:{sender_id}'),
                    InlineKeyboardButton("❌ Block", callback_data=f'user_block:{sender_id}'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                attempt_str = f" (Reminder #{attempt-1})" if attempt > 1 else ""
                await self.application.bot.send_message(
                    chat_id=self.authorized_chat_id,
                    text=(
                        f"🛡️ *GATEKEEPER ALERT*{attempt_str}\n\n"
                        f"*New User:* `{sender_id}`\n"
                        f"*Message:* \"{message_text}\"\n\n"
                        f"Should I authorize this user to talk to me?"
                    ),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                # Wait for user input for the interval duration
                try:
                    await asyncio.wait_for(self.auth_response_event.wait(), timeout=float(retry_interval))
                    return self.last_auth_result
                except asyncio.TimeoutError:
                    logger.info(f"Authorization attempt {attempt} for {sender_id} timed out. Retrying...")
                    continue

            except Exception as e:
                logger.error(f"Error in user auth loop (Attempt {attempt}): {e}")
                await asyncio.sleep(10) # Wait a bit before retry if error
        
        logger.warning(f"Authorization for {sender_id} reached 1-hour limit. Blocking.")
        return False

    async def request_financial_authorization(self, amount: float, description: str):
        """
        Sends a message with Approve/Deny buttons for a financial transaction.
        Waits for 5 minutes (300 seconds) for response.
        """
        if not self.application or not self.authorized_chat_id:
            logger.error("Telegram Service not fully initialized. Cannot request financial auth.")
            return False

        self.auth_response_event.clear()
        self.last_auth_result = None

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve Transaction", callback_data='fin_approve'),
                InlineKeyboardButton("❌ Deny", callback_data='fin_deny'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await self.application.bot.send_message(
                chat_id=self.authorized_chat_id,
                text=(
                    f"⚠️ *FINANCIAL APPROVAL REQUIRED*\n\n"
                    f"{description}\n\n"
                    f"*Amount:* ₹{amount}\n\n"
                    f"Do you authorize this transaction?"
                ),
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            try:
                await asyncio.wait_for(self.auth_response_event.wait(), timeout=300.0)
                return self.last_auth_result
            except asyncio.TimeoutError:
                logger.warning("Financial authorization request timed out.")
                await self.application.bot.send_message(
                    chat_id=self.authorized_chat_id,
                    text=f"⏳ Authorization for ₹{amount} timed out (5 minutes). Access denied automatically."
                )
                return False

        except Exception as e:
            logger.error(f"Error in request_financial_authorization: {e}")
            return False

    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles button clicks for Approve/Deny."""
        query = update.callback_query
        await query.answer()

        data = query.data
        
        if data.startswith('user_allow:'):
            user_id = data.split(':')[1]
            self.last_auth_result = True
            await query.edit_message_text(text=f"✅ User `{user_id}` has been AUTHORIZED by Boss.")
        elif data.startswith('user_block:'):
            user_id = data.split(':')[1]
            self.last_auth_result = False
            await query.edit_message_text(text=f"❌ User `{user_id}` has been BLOCKED by Boss.")
        elif query.data == 'auth_approve':
            self.last_auth_result = True
            await query.edit_message_caption(caption="✅ Access GRANTED by Boss.")
        elif query.data == 'auth_deny':
            self.last_auth_result = False
            await query.edit_message_caption(caption="❌ Access DENIED by Boss.")
        elif query.data == 'fin_approve':
            self.last_auth_result = True
            await query.edit_message_text(text="✅ Financial Transaction APPROVED by Boss.")
        elif query.data == 'fin_deny':
            self.last_auth_result = False
            await query.edit_message_text(text="❌ Financial Transaction DENIED by Boss.")

        self.auth_response_event.set()

    async def send_voice_note(self, chat_id: str, text: str):
        """Generates a voice file and sends it as a Telegram Voice Note."""
        if not self.application: return
        
        try:
            # Generate the voice file
            audio_path = await self.voice_speaker.generate_voice_file(text)
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as voice:
                    await self.application.bot.send_voice(
                        chat_id=chat_id,
                        voice=voice,
                        caption=text[:100] + "..." if len(text) > 100 else text
                    )
                # Cleanup
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Failed to send voice note: {e}")
            # Fallback to text
            await self.application.bot.send_message(chat_id=chat_id, text=text)

    async def stop(self):
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
