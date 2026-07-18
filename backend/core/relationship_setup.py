"""
First-Time Setup — User teaches the system who everyone is.
Run this once. Add people any time after.
"""

from core.people_registry import PeopleRegistry, Person
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()
reg     = PeopleRegistry()

def setup_wizard():
    """Interactive wizard to populate the People Registry."""
    console.print("\n[bold magenta]👥 People Registry Setup Wizard[/bold magenta]")
    console.print("[dim]Teach IQ-Core who the people in your life are.[/dim]\n")

    while True:
        console.print("[bold cyan]➕ Add a new person[/bold cyan]")

        name     = Prompt.ask("  Their name")
        nickname = Prompt.ask("  Nickname (or press Enter to skip)", default=name)

        console.print("\n  Relationship types:")
        console.print("  [dim]grandparent, parent, annaya, akka, younger_sibling,")
        console.print("  teacher, professor, boss, elder_community, close_friend,")
        console.print("  classmate, colleague, child_student, elder_relative, acquaintance[/dim]")
        rel_type = Prompt.ask("  Relationship type")

        age_group = Prompt.ask(
            "  Age group",
            choices=["child", "teen", "young_adult", "adult", "elder"],
            default="adult"
        )

        lang = Prompt.ask(
            "  Preferred language",
            choices=["english", "telugu", "hindi", "mixed"],
            default="english"
        )

        topics_care  = Prompt.ask("  Topics they care about (comma separated)").split(",")
        topics_avoid = Prompt.ask("  Topics to AVOID (comma separated)").split(",")

        help_style = Prompt.ask(
            "  How do they prefer to receive help?",
            choices=["direct_advice", "just_listen", "ask_questions"],
            default="direct_advice"
        )

        notes = Prompt.ask("  Any special notes? (health, personality, triggers)", default="")

        person = Person(
            name=name.strip(),
            nickname=nickname.strip(),
            relationship_type=rel_type.strip(),
            age_group=age_group.strip(),
            emotional_state="neutral",
            preferred_language=lang.strip(),
            topics_they_care_about=[t.strip() for t in topics_care],
            topics_to_avoid=[t.strip() for t in topics_avoid],
            how_they_prefer_to_be_helped=help_style,
            last_interaction="never",
            notes=notes,
            respect_level_required=0.0
        )

        reg.add_person(person)
        console.print(f"\n  [green]✅ {name} added to your People Registry![/green]\n")

        if not Confirm.ask("Add another person?"):
            break

    console.print("\n[bold green]🎉 People Registry setup complete![/bold green]")
    console.print(f"[dim]Total people registered: {len(reg.get_all_people())}[/dim]")


# ── Pre-Populated Starter Registry ────────────────────────────────────────────
def load_default_relationships():
    """
    Pre-loads the most common relationship types with good defaults.
    User can override any of these.
    """
    defaults = [
        Person("Thatha",   "Nana",    "grandparent",     "elder",       "neutral", "telugu",  ["stories","health","family"], ["arguments","technology"], "just_listen",   "never", "Hard of hearing. Speak slowly and clearly.", 1.0),
        Person("Ammamma",  "Nana",    "grandparent",     "elder",       "neutral", "telugu",  ["cooking","family","god"],    ["politics","money"],       "just_listen",   "never", "Gets emotional easily. Be extra gentle.",   1.0),
        Person("Nanna",    "Dad",     "parent",          "adult",       "neutral", "mixed",   ["work","family","cricket"],   ["laziness","failures"],    "direct_advice", "never", "Values hard work and responsibility.",       0.98),
        Person("Amma",     "Mom",     "parent",          "adult",       "neutral", "mixed",   ["food","health","studies"],   ["stress","arguments"],     "just_listen",   "never", "Worries a lot — reassure often.",           0.98),
        Person("Annaya",   "Bhai",    "annaya",          "young_adult", "neutral", "mixed",   ["tech","gaming","career"],    ["being doubted"],          "direct_advice", "never", "Elder brother — listen to his experience.", 0.90),
        Person("Akka",     "Didi",    "akka",            "young_adult", "neutral", "mixed",   ["studies","future","family"], ["comparisons"],            "ask_questions", "never", "Elder sister — very caring and protective.", 0.90),
        Person("Teacher",  "Sir",     "teacher",         "adult",       "neutral", "english", ["academics","discipline"],    ["excuses","disrespect"],   "direct_advice", "never", "Always address as Sir/Ma'am.",              0.97),
        Person("BestFriend","Bro",    "close_friend",    "young_adult", "neutral", "mixed",   ["gaming","movies","life"],    [],                         "just_listen",   "never", "Can be fully honest with them.",            0.60),
        Person("Classmate", "Yaar",   "classmate",       "teen",        "neutral", "mixed",   ["studies","fun","projects"],  [],                         "direct_advice", "never", "",                                          0.65),
        Person("SmallKid", "Chotu",  "younger_sibling", "child",       "neutral", "mixed",   ["games","stories","school"],  ["scary topics"],           "ask_questions", "never", "Needs encouragement. Simple language only.", 0.60),
    ]

    for person in defaults:
        reg.add_person(person)
        console.print(f"  [dim]✓ Loaded: {person.name} ({person.relationship_type})[/dim]")

    console.print(f"\n[green]✅ {len(defaults)} default relationships loaded.[/green]")


if __name__ == "__main__":
    import sys
    if "--defaults-only" in sys.argv:
        load_default_relationships()
    elif "--wizard" in sys.argv:
        setup_wizard()
    else:
        load_default_relationships()
        setup_wizard()
