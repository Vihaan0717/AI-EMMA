// utils/teluguPatterns.js

const teluguPatterns = {

  // ============================================
  // 1. GREETINGS (100+ words)
  // ============================================
  greetings: [
    // Standard Greetings
    'namaskaram', 'namasthe', 'namaste', 'hello', 'hi', 'hii', 'hiii',
    'hey', 'heyyy', 'sup', 'wassup', 'whatsup', 'what\'s up',
    'howdy', 'yo', 'yoo', 'yooo',
    
    // Telugu Greetings
    'ela unnav', 'ela unnaru', 'ela unav', 'ela unaru',
    'ela unnadi', 'bagunava', 'bagunara', 'bagunnava', 'bagunnara',
    'ela undi', 'em chestunnav', 'em chestunav', 'em chestunnaru',
    'em chestunavv', 'em chestaru', 'em chesav',
    
    // Rajamahendravaram (Rajahmundry) Slang
    'em ra', 'em ma', 'em anna', 'em akka', 'em babu',
    'em andi', 'em bro', 'em sis', 'enti ra', 'enti ma',
    'enti anna', 'enti bro', 'em da', 'em di',
    'ra em', 'ma em', 'em le', 'em lo',
    'ela ra', 'ela ma', 'ela da', 'ela di',
    'bagunnava ra', 'bagunnara ma', 'ela unnav ra',
    
    // Hyderabad Slang
    'kya baat hai', 'kya haal hai', 'sab theek',
    'kyun bhai', 'kaise ho', 'kya chal raha',
    'bhai kya scene hai', 'scene em undi',
    'yaar ela unnav', 'dost ela unnav',
    'bhai wassup', 'machaan ela unnav',
    
    // Time based greetings
    'good morning', 'good afternoon', 'good evening', 'good night',
    'subhodayam', 'shubhodayam', 'subha raatri', 'shubha raatri',
    'morning ra', 'morning ma', 'morning bro',
    'night ra', 'night ma', 'night bro',
    'gm', 'gn', 'gm ra', 'gn ra',
    
    // Casual Check-ins
    'enti vishayam', 'em vishayam', 'em samacharam',
    'em jarigindi', 'em jarigiindi', 'em news',
    'em update', 'updates em', 'cheppandi em jarigindi',
    'long time', 'chala rojulu aindi', 'chala time aindi',
    'kanapadadam ledu', 'kanapadadam leda',
    'ekkada unnav', 'ekkada unaru', 'ekkada unnaru'
  ],

  // ============================================
  // 2. FAREWELLS (80+ words)
  // ============================================
  farewells: [
    // Standard
    'bye', 'bye bye', 'babye', 'bbye', 'byee', 'byeee',
    'goodbye', 'good bye', 'ciao', 'alvida', 'tata',
    'later', 'laters', 'ttyl', 'ttys', 'talk later',
    
    // Telugu Farewells
    'veltunna', 'veltunnanu', 'veltuna', 'velutunna',
    'vellipotunna', 'vellali', 'vellipothunna',
    'ippudu veltanu', 'ippude veltunna',
    'maatladdam', 'malli maatladdam', 'malli kaluddam',
    'malli chustam', 'malli chuddam', 'malli kalustam',
    'ok veltunna', 'sare veltunna', 'aythe veltunna',
    
    // Rajamahendravaram Style
    'velta ra', 'velta ma', 'velta bro', 'velta anna',
    'veltunna ra', 'veltunna ma', 'veltunna bro',
    'ok ra bye', 'ok ma bye', 'ok bro bye',
    'chustam ra', 'chustam ma', 'chusta ra', 'chusta ma',
    'malli chustam ra', 'malli chustam ma',
    
    // Hyderabad Style
    'chalte hain', 'chalta hoon', 'nikalta hoon',
    'baad mein baat karte', 'phir milenge',
    'ok yaar bye', 'ok bhai bye', 'ok dost bye',
    'niklo yaar', 'chalte chalte', 'baad mein',
    
    // Casual
    'ok take care', 'take care ra', 'take care ma',
    'tc ra', 'tc ma', 'tc bro', 'tc anna',
    'all the best', 'atb', 'best of luck',
    'catch ya', 'catch you later', 'later bro',
    'peace', 'peace out', 'deuces'
  ],

  // ============================================
  // 3. AFFIRMATIONS (100+ words)
  // ============================================
  affirmations: [
    // Standard
    'yes', 'yeah', 'yep', 'yup', 'yess', 'yesss',
    'ok', 'okay', 'ok ok', 'okk', 'okkk',
    'sure', 'surely', 'definitely', 'absolutely',
    'of course', 'ofcourse', 'ofc', 'obvio',
    'right', 'correct', 'exactly', 'precisely',
    'true', 'true true', 'so true', 'facts',
    
    // Telugu Affirmations
    'avunu', 'avunuu', 'avunuuu', 'avunav',
    'sare', 'saree', 'sarele', 'sare sare',
    'aythe', 'ayte', 'aythe sare', 'aythe ok',
    'ante', 'ante sare', 'ante ok',
    'chestanu', 'chestam', 'chestunna',
    'agree', 'agree avutunna', 'agree ra',
    'thelusindi', 'telisindi', 'telusu', 'telsu',
    'got it', 'got it ra', 'got it bro',
    'understood', 'clear', 'clear ra', 'clear bro',
    'alage', 'alage chestanu', 'alage chestha',
    'no problem', 'np', 'no prob', 'no issue',
    'chestam ra', 'chestam ma', 'chestam bro',
    
    // Rajamahendravaram Style
    'avunu ra', 'avunu ma', 'avunu bro', 'avunu anna',
    'sare ra', 'sare ma', 'sare bro', 'sare anna',
    'ok ra', 'ok ma', 'ok bro', 'ok anna',
    'ayyindi ra', 'ayyindi ma', 'ayyindi bro',
    'chestha ra', 'chestha ma', 'chestha bro',
    
    // Hyderabad Style
    'haan bhai', 'haan yaar', 'bilkul', 'zaroor',
    'pakka', 'pakka bhai', 'pakka yaar',
    'done bhai', 'done yaar', 'ho jayega',
    'kar deta hoon', 'kar dunga',
    'theek hai', 'theek hai bhai', 'sahi hai',
    
    // Slang Affirmations
    'aite', 'aight', 'bet', 'fasho', 'fosho',
    'word', 'word up', 'legit', 'valid',
    'ikr', 'fr', 'fr fr', 'no cap', 'real talk',
    'cheppindi correct', 'cheppindi nijam'
  ],

  // ============================================
  // 4. NEGATIONS (80+ words)
  // ============================================
  negations: [
    // Standard
    'no', 'nope', 'nah', 'nay', 'never',
    'not', 'no way', 'absolutely not', 'definitely not',
    'impossible', 'cant', "can't", 'cannot', 'won\'t',
    
    // Telugu Negations
    'ledu', 'ledhu', 'ladu', 'ledha',
    'ledu ra', 'ledu ma', 'ledu bro', 'ledu anna',
    'vaddu', 'vaddhu', 'vaddu ra', 'vaddu ma',
    'kaadu', 'kadu', 'kadhu', 'kaadhu',
    'kaadu ra', 'kaadu ma', 'kaadu bro',
    'jarigadu', 'jarigaledu', 'jarigadhu',
    'cheyanu', 'cheyyanu', 'cheyyanee',
    'raadu', 'raledhu', 'raledu', 'radu',
    'undadu', 'undadhu', 'untundadu',
    'em ledu', 'em ledu bro', 'em ledu ra',
    'em ledu ma', 'em undadu', 'em cheyyadhu',
    
    // Rajamahendravaram Style
    'ledu ra', 'ledu ma', 'vaddu ra', 'vaddu ma',
    'kaadu ra', 'kaadu ma', 'em kaadu ra',
    'cheyyadhu ra', 'vaddhu ra', 'vaddhu ma',
    'poni ra', 'poni ma', 'poni bro',
    'ayyedu ra', 'ayyedu ma', 'ayyeledhu',
    
    // Hyderabad Style
    'nahi bhai', 'nahi yaar', 'bilkul nahi',
    'mat karo yaar', 'kya yaar', 'nahi hoga',
    'impossible hai', 'nahi nahi', 'kabhi nahi',
    
    // Slang Negations
    'nope ra', 'nope ma', 'nah ra', 'nah bro',
    'poni', 'poni ley', 'poni lede', 'em poni',
    'em ayina poni', 'poni vidhu', 'vidhu ra'
  ],

  // ============================================
  // 5. URGENCY & IMPATIENCE (100+ words)
  // ============================================
  urgency: [
    // Standard Urgency
    'urgent', 'urgently', 'asap', 'immediately',
    'right now', 'right away', 'instantly',
    'hurry', 'hurry up', 'quick', 'quickly',
    'fast', 'faster', 'speed up', 'rush',
    
    // Telugu Urgency
    'inka antha sepu', 'inka entha sepu', 'inka entho sepu',
    'jaldi', 'jaldi ra', 'jaldi ma', 'jaldi bro',
    'reply ivvu', 'reply ivvandi', 'reply cheyyi',
    'cheppandi', 'cheppu ra', 'cheppu ma',
    'teesikuntav', 'teesikuntaru', 'teesikuntav em',
    'ippude cheyyi', 'ippude cheseyyi', 'ippude cheppandi',
    'waiting', 'wait chestunna', 'wait chestunnanu',
    'chala sepu aindi', 'chala time aindi', 'chala wait chesanu',
    'reply ra', 'reply ma', 'reply bro', 'reply anna',
    'chudatledu', 'chudaledu', 'chudatledhu',
    'message chusav', 'chusara', 'open chesav',
    'inka entha', 'enni sarlu cheppali', 'enduku cheppataledhu',
    'chala late', 'chala late aindi', 'time waste',
    'late aindi', 'chala late ayyindi', 'late avutundi',
    'em chestunnav', 'em chestunavv', 'pani cheyyi',
    'velu velu', 'speed up ra', 'fast ra', 'fast ma',
    
    // Rajamahendravaram Urgency Slang
    'em ra time waste', 'enduku ra delay',
    'cheppu ra jaldi', 'cheppu ma jaldi',
    'ra em chestunnav', 'ma em chestunnav',
    'aa ra jaldi', 'aa ma jaldi',
    'pampinchav ra', 'pampinchav ma',
    'chalu ra ippude', 'chalu ma ippude',
    'vaddhu ra time waste', 'time waste vaddhu',
    
    // Hyderabad Urgency
    'jaldi karo yaar', 'jaldi karo bhai',
    'abhi karo', 'abhi batao', 'abhi reply karo',
    'ek dum jaldi', 'bahut time ho gaya',
    'kitna time lagega', 'kab karoge',
    'reply karo yaar', 'batao na', 'bolo na',
    
    // Frustration words
    'frustrating', 'frustrated', 'irritating',
    'annoying', 'enough', 'stop delaying',
    'last warning', 'oka saari cheppandi',
    'malli cheppala', 'enni sarlu',
    'chalu chalu', 'ayyindi ayy'
  ],

  // ============================================
  // 6. RENT & HOUSING (100+ words)
  // ============================================
  rent: [
    // Standard
    'rent', 'rental', 'monthly rent', 'rent amount',
    'house rent', 'flat rent', 'room rent', 'pg rent',
    
    // Telugu Rent Words
    'addhe', 'adde', 'addhe evvalo', 'addhe entha',
    'nela addhe', 'nela ki addhe', 'monthly addhe',
    'intaki addhe', 'illu addhe', 'flat ki addhe',
    'apartment ki addhe', 'room ki addhe',
    'rent evvalo', 'rent entha', 'rent cheppandi',
    'rent fix ayyinda', 'rent confirm ayyinda',
    'rent pay chesam', 'rent katham', 'rent katham chesam',
    'rent pampinchanu', 'rent transfer chesanu',
    
    // Housing Types
    'illu', 'intiki', 'flat', 'apartment', 'room',
    'house', 'home', 'pg', 'hostel', '1bhk', '2bhk',
    '3bhk', 'studio', 'duplex', 'villa', 'independent house',
    'sharing room', 'single room', 'double room',
    'attached bathroom', 'common bathroom',
    
    // Availability
    'flat available na', 'room available na',
    'vacancy unda', 'vacancy undi', 'available ga unda',
    'ela undi', 'condition ela undi', 'house ela undi',
    'fresh house', 'newly painted', 'newly renovated',
    'furnished', 'semi furnished', 'unfurnished',
    
    // Location
    'ekkada undi', 'address em', 'location em',
    'area em', 'near to', 'bus stop dakkara',
    'school dakkara', 'hospital dakkara',
    'market dakkara', 'ikkade dakkara',
    
    // Advance & Deposit
    'advance', 'deposit', 'advance evvalo',
    'deposit evvalo', 'advance katham',
    'refundable', 'non refundable',
    '1 month advance', '2 month advance',
    '3 month advance', 'token advance',
    
    // Negotiation
    'negotiate avutunda', 'reduce cheyagalara',
    'discount unda', 'less cheyagalara',
    'final amount em', 'best price em',
    'any offer', 'special offer'
  ],

  // ============================================
  // 7. PAYMENT (100+ words)
  // ============================================
  payment: [
    // Standard
    'payment', 'pay', 'paid', 'paying',
    'money', 'amount', 'transfer', 'send money',
    'receive', 'received', 'transaction',
    
    // Telugu Payment
    'paisa', 'paisalu', 'rupees', 'rupayilu',
    'pay cheyali', 'pay chesam', 'pay aindi',
    'money pampinchanu', 'amount transfer chesanu',
    'payment chesam', 'payment ayyinda',
    'receipt unda', 'bill unda', 'invoice unda',
    
    // Payment Apps
    'gpay', 'google pay', 'phonepe', 'phone pe',
    'paytm', 'upi', 'bhim', 'neft', 'rtgs', 'imps',
    'netbanking', 'net banking', 'online transfer',
    'bank transfer', 'cash', 'cash payment',
    'cheque', 'check', 'dd', 'demand draft',
    
    // Payment Status
    'pending', 'due', 'overdue', 'late fee',
    'balance', 'outstanding', 'clear chesam',
    'settle chesam', 'dues clear', 'payment done',
    'payment failed', 'payment pending',
    'payment successful', 'payment complete',
    
    // UPI Details
    'upi id', 'account number', 'ifsc code',
    'bank name', 'account holder name',
    'transaction id', 'reference number',
    'screenshot pampinchu', 'proof pampinchu',
    
    // Hyderabad Payment Slang
    'paise bhejo yaar', 'abhi bhejo',
    'payment kar do', 'transfer kar do',
    'ek dum bhejo', 'jaldi bhejo',
    'bahut din ho gaye', 'pay karo na',
    
    // Rajamahendravaram Payment
    'paisa pampinchu ra', 'paisa ivvu ra',
    'money pampinchu ma', 'money ivvu ma',
    'pay cheseyyi ra', 'pay cheseyyi ma',
    'katham ra', 'katham ma', 'kattinchandi'
  ],

  // ============================================
  // 8. MAINTENANCE & REPAIRS (100+ words)
  // ============================================
  maintenance: [
    // Standard
    'problem', 'issue', 'repair', 'fix', 'broken',
    'damage', 'damaged', 'not working', 'faulty',
    'maintenance', 'service', 'check', 'inspect',
    
    // Telugu Maintenance
    'problem undi', 'issue undi', 'pani cheyyatledu',
    'cheddupoyindi', 'chesipoyindi', 'break ayyindi',
    'fix cheseyyi', 'repair cheseyyi', 'correct cheseyyi',
    'chudandi', 'chusandi', 'pampinchandi',
    
    // Water Issues
    'water leakage', 'water leak', 'seepage',
    'water problem', 'water issue',
    'neeruchindi', 'water pothundi', 'pipe burst',
    'tap leaking', 'tap pani cheyyatledu',
    'water supply ledu', 'water ravadam ledu',
    'borewell problem', 'motor pani cheyyatledu',
    'water tank problem', 'water pressure ledu',
    'neeru ravadam ledu', 'neeru problem',
    
    // Electrical Issues
    'current ledu', 'current poyindi', 'light ledu',
    'electricity problem', 'power cut', 'power failure',
    'trip ayyindi', 'fuse poyindi', 'wire problem',
    'short circuit', 'switch pani cheyyatledu',
    'plug pani cheyyatledu', 'socket problem',
    'meter problem', 'eb problem', 'power issue',
    'fan pani cheyyatledu', 'fan problem',
    'ac pani cheyyatledu', 'ac problem', 'ac service',
    'light pani cheyyatledu', 'bulb cheddipoyindi',
    'inverter problem', 'generator problem',
    
    // Plumbing
    'plumber', 'plumbing problem', 'bathroom problem',
    'toilet problem', 'commode problem', 'flush pani cheyyatledu',
    'drain blocked', 'pipe choked', 'pipe blocked',
    'sink blocked', 'washbasin problem',
    'geyser problem', 'hot water ledu', 'shower problem',
    
    // Structural
    'roof leaking', 'wall crack', 'ceiling problem',
    'floor problem', 'door problem', 'window problem',
    'door lock problem', 'lock pani cheyyatledu',
    'door jam ayyindi', 'window break ayyindi',
    'paint poyyindi', 'plaster poyyindi',
    'seepage problem', 'damp walls', 'moisture problem',
    
    // Appliances
    'refrigerator problem', 'fridge problem',
    'washing machine problem', 'tv problem',
    'microwave problem', 'oven problem',
    'geyser problem', 'water heater problem',
    
    // Professionals Needed
    'carpenter', 'plumber', 'electrician',
    'painter', 'mason', 'contractor',
    'service person', 'mechanic', 'technician',
    'pampinchandi', 'pampinchaali', 'pampinchu'
  ],

  // ============================================
  // 9. COMPLAINTS (100+ words)
  // ============================================
  complaints: [
    // Standard
    'complaint', 'complain', 'issue', 'problem',
    'unhappy', 'dissatisfied', 'disappointed',
    'frustrated', 'angry', 'upset', 'irritated',
    
    // Telugu Complaints
    'complaint undi', 'chala problem undi',
    'chala kastam', 'chala trouble',
    'bayatapettandi', 'cheppali anipistundi',
    'chala chikaku ga undi', 'chikaku ga undi',
    
    // Noise Complaints
    'noise', 'sound chala undi', 'noise chala',
    'disturbance', 'disturbing', 'too loud',
    'chala sound', 'chala noise', 'quiet ga ledu',
    'music chala loud ga undi', 'party noise',
    'night lo noise', 'late night noise',
    'neighbours noise', 'upstairs noise',
    'pakkinti vallu noise', 'sound problem',
    
    // Neighbor Complaints
    'neighbors', 'neighbour', 'pakkinti vallu',
    'pakkinti vallu problem', 'neighbours fight',
    'fight jarugutundi', 'quarrel jarugutundi',
    'pakkinti vallu disturb chestunnaru',
    'upstairs people problem', 'downstairs people',
    'common area problem', 'corridor problem',
    
    // Security Complaints
    'security ledu', 'safety ledu', 'safe ledu',
    'dangerous', 'unsafe', 'security problem',
    'theft', 'stealing', 'missing items',
    'suspicious person', 'outsider vacharu',
    'gate open ga undi', 'lock ledu',
    'cctv pani cheyyatledu', 'cctv problem',
    'security guard ledu', 'watchman ledu',
    
    // Cleanliness Complaints
    'dirty', 'clean ledu', 'cleaning ledu',
    'garbage', 'dustbin problem', 'waste problem',
    'smell vastundi', 'bad smell', 'stink',
    'cockroach', 'cockroaches', 'pests',
    'rats', 'mice', 'mosquitoes', 'insects',
    'ants', 'lizards', 'spiders',
    'bathroom dirty', 'common area dirty',
    'corridor dirty', 'staircase dirty',
    
    // Management Complaints
    'owner response ledu', 'owner reply ledu',
    'nobody responding', 'no action taken',
    'problem fix kaledu', 'repair kaledu',
    'promise chesi cheyyaledu', 'time waste',
    'chala rojulu ayyindi', 'fix kavatledu',
    
    // Hyderabad Complaint Slang
    'bahut problem hai yaar', 'kya scene hai',
    'yaar ye kya hai', 'bhai sun na',
    'koi sun nahi raha', 'problem solve nahi ho raha',
    'action nahi le rahe', 'baat nahi kar rahe',
    
    // Rajamahendravaram Complaint Slang
    'ra chala problem', 'ma chala issue',
    'em ra ee problem', 'em ma ee issue',
    'chala kastam ra', 'chala kastam ma',
    'ila ayithe ela ra', 'ila ayithe ela ma'
  ],

  // ============================================
  // 10. APPRECIATION (80+ words)
  // ============================================
  appreciation: [
    // Standard
    'thanks', 'thank you', 'thankyou', 'thankful',
    'grateful', 'appreciate', 'appreciated',
    'great', 'good', 'nice', 'excellent', 'perfect',
    'wonderful', 'fantastic', 'amazing', 'awesome',
    'brilliant', 'superb', 'outstanding', 'exceptional',
    
    // Telugu Appreciation
    'dhanyavaadalu', 'dhanyavaadamulu', 'thanks ra',
    'chala bagundi', 'chala baagundi', 'super',
    'super ra', 'super ma', 'super bro', 'super anna',
    'chala helpful', 'helpful anna', 'helpful akka',
    'meeru chala bagunnaru', 'meeru helpful ga unnaru',
    'chala manchidi', 'manchidi', 'bavundi',
    'chala bavundi', 'bagundi', 'baagundi',
    'chala thanks', 'bhale chesaru', 'bhale cheshav',
    'okka saari thanks', 'mee help ki thanks',
    
    // Rajamahendravaram Appreciation
    'bhale ra', 'bhale ma', 'bhale bro', 'bhale anna',
    'super ra thanks', 'super ma thanks',
    'chala manchiga chesav ra', 'chala manchiga chesav ma',
    'thanks ra bro', 'thanks ma akka',
    'meeru chala manchi vallu ra', 'manchi vallu',
    
    // Hyderabad Appreciation
    'bahut acha hai yaar', 'bahut badhiya',
    'mast hai bhai', 'bindas hai',
    'ek dum mast', 'kya baat hai',
    'shukriya yaar', 'shukriya bhai',
    'bohot acha kiya', 'wah wah',
    
    // Emoji expressions
    '👍', '🙏', '❤️', '😊', '😍',
    'love it', 'love this', 'keep it up',
    'well done', 'good job', 'nice work'
  ],

  // ============================================
  // 11. QUESTIONS (100+ words)
  // ============================================
  questions: [
    // Standard
    'what', 'how', 'where', 'when', 'why', 'who',
    'which', 'whose', 'whom', 'whatever', 'however',
    'is it', 'are you', 'do you', 'can you',
    'will you', 'would you', 'could you', 'should',
    
    // Telugu Questions
    'enti', 'emi', 'ela', 'ekkada', 'evaru',
    'enduku', 'entha', 'eppudu', 'evvaro',
    'evvariki', 'emiti', 'ela cheyali',
    'cheppagalaru', 'cheppu', 'cheppandi',
    'telustha', 'telustunaara', 'em vishayam',
    'adi enti', 'adi em', 'adi ela',
    'ikkada ledu em', 'cheppara em',
    'em jarigindi', 'ela jarigindi',
    'ekkada jarigindi', 'evaru chesaru',
    
    // Information Seeking
    'details cheppandi', 'information ivvandi',
    'elaborate cheyandi', 'explain cheyandi',
    'clarify cheyandi', 'confirm cheyandi',
    'details em', 'more details', 'full details',
    'complete information', 'specs em',
    
    // Rajamahendravaram Questions
    'em ra', 'em ma', 'ela ra', 'ela ma',
    'ekkada ra', 'ekkada ma', 'eppudu ra',
    'evaru ra', 'evaru ma', 'enduku ra',
    'entha ra', 'entha ma', 'em ayyindi ra',
    
    // Hyderabad Questions
    'kya baat hai yaar', 'kya hua bhai',
    'kab hoga', 'kaise hoga', 'kahan hai',
    'kaun hai', 'kyun kiya', 'kitna hai',
    'bolo na yaar', 'batao na bhai',
    
    // Rhetorical
    'serious ga', 'seriously', 'really',
    'sachama', 'nijamga', 'nammali',
    'sure na', 'confirm na', 'pakka na'
  ],

  // ============================================
  // 12. AVAILABILITY (80+ words)
  // ============================================
  availability: [
    // Standard
    'available', 'free', 'busy', 'occupied',
    'online', 'offline', 'active', 'inactive',
    'present', 'absent', 'here', 'there',
    
    // Telugu Availability
    'available na', 'unnara', 'unnava',
    'free ga unnara', 'busy ga unnara',
    'eppudu untaru', 'eppudu free',
    'meet avvagalara', 'call cheyyocha',
    'visit cheyyocha', 'ravocha', 'ravachcha',
    'ikkade unnara', 'ekkada unnaru',
    'ikkade unava', 'ekkada unavu',
    'time unda', 'time undha',
    'free time unda', 'available time unda',
    
    // Meeting
    'meet chedam', 'meet avudham', 'kaludham',
    'visit cheyali', 'site visit', 'flat visit',
    'chudali', 'choodam', 'inspekt chedam',
    'come and see', 'aa chusuko',
    'ikkade ra oka saari', 'ikkade ma oka saari',
    
    // Timing
    'morning free na', 'evening free na',
    'weekend free na', 'tomorrow free na',
    'today possible na', 'when possible',
    'eppudu convenient', 'convenient time em',
    'schedule em', 'timing em'
  ],

  // ============================================
  // 13. DOCUMENTS & AGREEMENTS (80+ words)
  // ============================================
  documents: [
    // Standard
    'documents', 'papers', 'paperwork', 'documentation',
    'agreement', 'contract', 'bond', 'lease',
    'proof', 'certificate', 'id', 'verification',
    
    // Telugu Documents
    'documents kavali', 'papers kavali',
    'agreement sign cheseyyi', 'contract sign cheseyyi',
    'documents pampinchu', 'papers pampinchu',
    'verification kavali', 'kyc kavali',
    
    // ID Documents
    'aadhar', 'aadhar card', 'aadhar number',
    'pan card', 'pan number', 'passport',
    'driving license', 'voter id', 'voter card',
    'ration card', 'electricity bill',
    'bank statement', 'salary slip',
    'office id', 'college id', 'student id',
    
    // Rental Documents
    'rental agreement', 'rent agreement',
    'lease agreement', 'license agreement',
    'police verification', 'tenant verification',
    'noc', 'no objection certificate',
    'stamp paper', 'notary', 'registration',
    'stamp duty', 'registration charges',
    
    // Process
    'sign cheseyyi', 'sign kavali', 'signature kavali',
    'notary cheseyyi', 'register cheseyyi',
    'submit cheseyyi', 'submit kavali',
    'original documents', 'xerox', 'photocopy',
    'scan cheseyyi', 'photo kavali', 'selfie kavali'
  ],

  // ============================================
  // 14. RAJAMAHENDRAVARAM SPECIFIC SLANG (100+)
  // ============================================
  rajahmundrySlang: [
    // Unique Rajahmundry words
    'em ra babu', 'em ma babu', 'em le babu',
    'ra babu', 'ma babu', 'anna babu',
    'bro em ra', 'bro em ma', 'bro ela unnav',
    'machaan', 'machaan ela unnav', 'machi',
    'dei', 'da', 'di', 'daa', 'dii',
    'ra dei', 'ma dei', 'bro dei',
    
    // Rajahmundry Expressions
    'arey', 'are', 'aree', 'arre',
    'arey ra', 'arey ma', 'arey bro',
    'bhai', 'bhaiya', 'anna', 'akka',
    'nanna', 'amma', 'ayya', 'sir',
    
    // Rajahmundry Common Phrases
    'em chestunnav ra', 'em chestunnav ma',
    'ela unnav ra', 'ela unnav ma',
    'enti ra', 'enti ma', 'enti bro',
    'em da', 'em di', 'em da bro',
    'cheppu ra', 'cheppu ma', 'cheppu bro',
    'vinara', 'vinnava', 'vinnara',
    'chusava', 'chusara', 'chusaru',
    'telusaa', 'telusara', 'telusava',
    
    // Rajahmundry Affirmations
    'sare le', 'ok le', 'avunu le',
    'ayte le', 'chestam le', 'chusta le',
    'chestha le', 'ok ok le', 'fine le',
    
    // Rajahmundry Negations  
    'ledu le', 'vaddu le', 'kaadu le',
    'poni le', 'em ledu le', 'vaddhu le',
    'em poni', 'poni ley', 'poni ledu',
    
    // Rajahmundry Curses/Strong Words (mild)
    'bokka', 'em bokka', 'pichi', 'pichi vaadu',
    'em pichi', 'pichi ga unnav', 'chala pichi',
    'vayya', 'em vayya', 'edava', 'edavalaa',
    'aagipomandi', 'aagipoyi', 'perlu',
    
    // Rajahmundry Food/Local References
    'gongura', 'pulihora', 'pesarattu', 'upma',
    'idli', 'dosa', 'vada', 'coffee', 'tea',
    'tiffin', 'meals', 'lunch', 'dinner', 'breakfast',
    
    // River/Local References
    'godavari', 'bridge', 'lalacheruvu', 'innespeta',
    'rajamahendravaram', 'rajahmundry', 'rajam',
    'dowleswaram', 'kovvur', 'tadepalligudem',
    
    // Local Transport
    'auto', 'auto ra', 'bus', 'train',
    'ola', 'uber', 'rapido', 'bike',
    'town bus', 'rta bus', 'private bus'
  ],

  // ============================================
  // 15. HYDERABAD SPECIFIC SLANG (100+)
  // ============================================
  hyderabadSlang: [
    // Unique Hyderabad/Dakhni words
    'kya scene hai', 'scene kya hai',
    'kyun bhai', 'kya yaar', 'yaar sun',
    'bhai sun', 'ek kaam kar', 'sun na',
    'bol na yaar', 'bata na bhai',
    
    // Hyderabad Expressions
    'seedha bol', 'sidha bol', 'straight point pe aa',
    'baat seedhi kar', 'clear kar',
    'kya matlab', 'matlab kya hai',
    'samajh nahi aaya', 'clear nahi hua',
    
    // Hyderabad Affirmations
    'haan haan', 'pakka pakka', 'done done',
    'theek hai theek hai', 'ho jayega ho jayega',
    'karta hoon', 'kar dunga', 'kar deta hoon',
    'bahut acha', 'bahut badhiya', 'mast hai',
    'bindas', 'fatafat', 'jhataput',
    
    // Hyderabad Negations
    'nahi nahi', 'bilkul nahi', 'kabhi nahi',
    'mat karo', 'karne ki zaroorat nahi',
    'chhodo yaar', 'jane do', 'chhed mat',
    
    // Hyderabad Food References
    'biryani', 'haleem', 'irani chai',
    'double ka meetha', 'lukhmi', 'kebab',
    'shawarma', 'paya', 'nihari',
    'paradise biryani', 'bawarchi', 'shadab',
    
    // Hyderabad Local References
    'charminar', 'golconda', 'hussain sagar',
    'banjara hills', 'jubilee hills', 'madhapur',
    'hitech city', 'gachibowli', 'secunderabad',
    'begumpet', 'ameerpet', 'dilsukhnagar',
    'kukatpally', 'miyapur', 'lb nagar',
    'uppal', 'hayathnagar', 'vanasthalipuram',
    
    // Hyderabad Transport
    'metro', 'mmts', 'city bus', 'rtc bus',
    'rapido', 'ola', 'uber', 'auto',
    'share auto', 'mini bus',
    
    // Hyderabad Mixed Language (Dakhni Urdu + Telugu)
    'kya re', 'kya va', 'kya ri',
    'arey yaar', 'yaar kya', 'bhai kya',
    'ek kaam kar yaar', 'ek cheez bata',
    'meri baat sun', 'meri problem sun',
    'kab aoge', 'kab aana', 'kab miloge',
    'milne aao', 'aa jao na', 'aa jao yaar',
    
    // Hyderabad Business Slang
    'deal pakka', 'deal done', 'deal karte hain',
    'final karte hain', 'close karte hain',
    'finalize karo', 'confirm karo',
    'advance bhejo', 'token bhejo',
    'agreement karo', 'sign karo'
  ],

  // ============================================
  // 16. EMOTIONS & FEELINGS (100+ words)
  // ============================================
  emotions: [
    // Happiness
    'happy', 'happyga', 'santhosham', 'santosham',
    'chala santhosham', 'chala happy', 'excited',
    'thrilled', 'overjoyed', 'ecstatic',
    'enjoy', 'enjoying', 'fun', 'funnyga',
    'laugh', 'haha', 'lol', 'lmao', 'rofl',
    'hahaha', 'hehe', 'hihi',
    
    // Sadness
    'sad', 'sadga', 'dukkham', 'chala sad',
    'upset', 'unhappy', 'depressed',
    'crying', 'cry', 'tears', 'heartbroken',
    '😢', '😭', '💔', '😞',
    
    // Anger
    'angry', 'anger', 'kopa', 'kopam',
    'chala kopam', 'irritated', 'frustrated',
    'annoyed', 'mad', 'furious', 'rage',
    'getting angry', 'dont make me angry',
    'kopam ga undi', 'chala irritating',
    
    // Surprise
    'wow', 'woww', 'wowww', 'omg', 'oh my god',
    'seriously', 'really', 'no way', 'what',
    'surprised', 'shocking', 'unbelievable',
    'ayyo', 'ayyoo', 'ayyyy', 'ore',
    'oreyyy', 'naa', 'naaaa',
    
    // Fear/Worry
    'scared', 'afraid', 'worried', 'tension',
    'tension ga undi', 'bhayam', 'chala bhayam',
    'anxious', 'stress', 'stressed',
    'dont know what to do', 'em cheyyalo teliadu',
    
    // Love/Affection
    'love', 'like', 'care', 'miss',
    'missing you', 'miss chestunna',
    'chala miss chestunna', 'prema', 'ishttam',
    
    // Boredom
    'bored', 'boring', 'em ledu', 'nothing to do',
    'timepass', 'em cheyyali teliadu',
    'vela ga undi', 'free ga undi',
    
    // Confusion
    'confused', 'em ardham kavatledu',
    'understand kaledu', 'clear kaadu',
    'em cheppataledhu', 'clear ga ledu',
    'doubt undi', 'doubt em'
  ],

  // ============================================
  // 17. INTERNET & TECH SLANG (80+ words)
  // ============================================
  techSlang: [
    // Social Media
    'dm', 'pm', 'message', 'chat', 'text',
    'call', 'video call', 'voice call',
    'whatsapp', 'telegram', 'instagram', 'facebook',
    'twitter', 'youtube', 'tiktok', 'snapchat',
    
    // Internet Slang
    'brb', 'afk', 'gtg', 'ttyl', 'nvm',
    'tbh', 'imo', 'imho', 'iirc', 'idk',
    'lol', 'lmao', 'rofl', 'omg', 'wtf',
    'smh', 'fwiw', 'fyi', 'btw', 'irl',
    'hmu', 'hit me up', 'reach me',
    
    // Telugu Tech Slang
    'net problem', 'wifi problem', 'network ledu',
    'signal ledu', 'data ledu', 'internet ledu',
    'phone chargeledu', 'battery ledu',
    'battery dead', 'phone off ayyindi',
    'call kavatadam ledu', 'network issue',
    'video call chedam', 'audio clear ledu',
    
    // Online Communication
    'send chesav', 'forward chesav', 'share chesav',
    'post chesav', 'upload chesav', 'download chesav',
    'screenshot send chesav', 'photo send chesav',
    'video send chesav', 'file send chesav',
    'link send chesav', 'location send chesav'
  ],

  // ============================================
  // 18. TIME EXPRESSIONS (80+ words)
  // ============================================
  timeExpressions: [
    // Standard Time
    'now', 'right now', 'immediately', 'instantly',
    'soon', 'shortly', 'in a while', 'later',
    'tomorrow', 'yesterday', 'today', 'tonight',
    'morning', 'afternoon', 'evening', 'night',
    'midnight', 'noon', 'midday',
    
    // Telugu Time
    'ippude', 'ippudu', 'ippi', 'ippatike',
    'konchem sepu', 'konchem time',
    'tharvata', 'tarvata', 'tarvata chestam',
    'repu', 'ninna', 'nedu', 'ee roju',
    'inta sepu', 'antha sepu', 'chala sepu',
    'ee vaaram', 'next week', 'ila poyina vaaram',
    'ee nela', 'next month', 'ila poyina nela',
    
    // Specific Times
    'morning 10 ki', 'afternoon 2 ki',
    'evening 5 ki', 'night 8 ki',
    'ippudu time em', 'eppudu convenient',
    'when free', 'free time lo',
    
    // Urgency Time
    'chala time aindi', 'chala rojulu aindi',
    'enni rojulu aindi', 'days ayyindi',
    'weeks ayyindi', 'months ayyindi',
    'waiting for long time', 'too long',
    'inka entho time', 'inka entha sepu'
  ],

  // ============================================
  // 19. COMMON TELUGU VERBS (100+ words)
  // ============================================
  teluguVerbs: [
    // Coming/Going
    'vastaanu', 'vastanu', 'vachanu', 'vachindi',
    'veltanu', 'velta', 'veltunna', 'vellaanu',
    'pampinchanu', 'pampistanu', 'pampistam',
    'ravachchu', 'raavachhu', 'raavachu',
    
    // Doing/Making
    'chestanu', 'chestha', 'chestam', 'chesanu',
    'chesam', 'cheyali', 'cheyyali', 'cheseyyi',
    'cheyagalanu', 'cheyyagalanu', 'cheyagalara',
    
    // Saying/Telling
    'cheppanu', 'cheppa', 'cheppali', 'cheppandi',
    'cheptunaanu', 'cheptunna', 'cheptunnam',
    'annanu', 'anna', 'antunna', 'antunnanu',
    
    // Seeing/Looking
    'chusanu', 'chusta', 'chustam', 'chusam',
    'chudali', 'chudalenu', 'chusthanu',
    'chudam', 'chuddam', 'chusukuntam',
    
    // Knowing/Understanding
    'telusunu', 'telusu', 'telisindi', 'telusindi',
    'ardham ayyindi', 'artham ayyindi',
    'arthamindi', 'ardhamindi',
    'teliadu', 'teliyadhu', 'telidhu',
    
    // Having/Getting
    'undanu', 'undi', 'undi ra', 'undha',
    'tesukuntanu', 'tesukunta', 'tesukuntam',
    'tecchaanu', 'techham', 'techanu',
    
    // Waiting
    'wait chestanu', 'wait chestunna',
    'waiting', 'chostunna', 'chustunna',
    'expect chestunna', 'waiting for reply',
    
    // Helping
    'help cheyali', 'help cheyyali', 'help chesam',
    'help chesanu', 'help chestanu', 'help ivvu',
    'support chesam', 'support cheyali',
    
    // Sending/Receiving
    'pampinchanu', 'pampistha', 'pampistham',
    'pampisthanu', 'pampinchali', 'pampinchandi',
    'receive chesanu', 'receive ayyindi',
    'vandindi', 'vachindi', 'chesindi'
  ],

  // ============================================
  // 20. NUMBERS & AMOUNTS (50+ words)
  // ============================================
  numbers: [
    // Telugu Numbers
    'okati', 'rendu', 'mudu', 'nalugu', 'aidu',
    'aaru', 'edu', 'enimidi', 'tommidi', 'padi',
    'padakondu', 'pannendu', 'padamuru',
    'padunalugu', 'padihenu',
    
    // Amount expressions
    'evvalo', 'entha', 'enta', 'entha avutundi',
    'total evvalo', 'grand total em', 'final amount em',
    'discount evvalo', 'offer price em',
    'original price em', 'market price em',
    
    // Common amounts
    '1000', '2000', '5000', '10000', '12000',
    '15000', '20000', '25000', '50000',
    'oka veyyi', 'rendu veyyi', 'ayidu veyyi',
    'padi veyyi', 'yabhai veyyi', 'lakh', 'lakhs',
    
    // Telugu Amount Words
    'veyyi', 'padiiveyyi', 'yabhaiveyyi',
    'laksham', 'lakshaladi', 'koti',
    'rupayilu', 'rupees', 'paisa', 'paisalu'
  ]
};

// ============================================
// EXPANDED TELUGU UNICODE PATTERNS
// ============================================
const teluguUnicodeRange = /[\u0C00-\u0C7F]/;

// ============================================
// TENGLISH SENTENCE STRUCTURES
// ============================================
const tenglishStructures = [
  // Verb patterns
  /\w+\s+(chesanu|chestanu|chestunna|chesam|cheyali)/i,
  /\w+\s+(undi|undadu|untundi|untundi)/i,
  /\w+\s+(vachindi|vastundi|vachchindi)/i,
  /\w+\s+(aindi|avutundi|ayindi|ayyindi)/i,
  /\w+\s+(ledu|ledhu|ladu|ledha)/i,
  /\w+\s+(annaru|antunnaru|chepparu)/i,
  /\w+\s+(pampinchanu|pampistha|pampistham)/i,
  /\w+\s+(veltunna|veltanu|vellaanu)/i,
  /\w+\s+(chustunna|chudali|chusam)/i,
  /\w+\s+(telusindi|telisindi|telusu)/i,
  
  // Question patterns
  /(em|emi|enti|ela|ekkada|evaru|enduku|entha|eppudu)\s+\w+/i,
  /\w+\s+(ra|ma|bro|anna|akka|andi)\s*\??/i,
  
  // Affirmation patterns
  /(sare|avunu|aythe|ok|chestam)\s+(ra|ma|bro|anna)?/i,
  
  // Negation patterns
  /(ledu|vaddu|kaadu|poni)\s+(ra|ma|bro|anna)?/i,
];

// ============================================
// WORD VARIATIONS & COMMON MISSPELLINGS
// ============================================
const wordVariations = {
  'avunu': ['avunu', 'avunuu', 'avun', 'awunu', 'awun'],
  'sare': ['sare', 'saree', 'sarele', 'sari', 'saari'],
  'ledu': ['ledu', 'ledhu', 'ladu', 'ledha', 'laedhu'],
  'vaddu': ['vaddu', 'vaddhu', 'vadu', 'vaddoo'],
  'cheyali': ['cheyali', 'cheyyali', 'cheali', 'chiali'],
  'chestunna': ['chestunna', 'chestuna', 'chestoona', 'chestona'],
  'namaskaram': ['namaskaram', 'namaskar', 'namaste', 'namasthe'],
  'dhanyavadalu': ['dhanyavadalu', 'dhanyavaadalu', 'danywadalu', 'thanks'],
};

module.exports = { 
  teluguPatterns, 
  teluguUnicodeRange,
  tenglishStructures,
  wordVariations
};
