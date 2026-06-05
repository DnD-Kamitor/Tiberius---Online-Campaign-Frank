"""
Tiberius Spellbook PDF Generator
Generates printable spell cards (2-up layout) for all of Tiberius's spells.
Run:  .venv/bin/python generate_spellbook.py
Out:  Tiberius-Spellbook.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Table, TableStyle, Paragraph, Spacer,
)
import os

# ── Palette (matches Tiberius-Ledger.pdf) ─────────────────────────────────────
PARCHMENT  = HexColor("#F5EDD6")
INK_DARK   = HexColor("#1A1008")
INK_MID    = HexColor("#3D2B0F")
RULE_COLOR = HexColor("#8B6914")
ACCENT     = HexColor("#5C3A1E")
HEADER_BG  = HexColor("#3D2B0F")
HEADER_FG  = HexColor("#F5EDD6")
SHADE_ROW  = HexColor("#EDE3C8")
FOOTER_BG  = HexColor("#C9A96E")

PAGE_W, PAGE_H = A4
LMARGIN = RMARGIN = 12 * mm
TMARGIN = 26 * mm
BMARGIN = 16 * mm
CONTENT_W = PAGE_W - LMARGIN - RMARGIN
CONTENT_H = PAGE_H - TMARGIN - BMARGIN

CHARACTER_NAME = "Tiberius Inscriptus Interlinearis"
CAMPAIGN       = "Frank's Campaign · Wizard 4 / Ranger 1 · Lvl 5"

CARD_W   = CONTENT_W / 2     # two columns
CARD_GAP = 3 * mm            # right-padding on left card (gap between the two)
CARD_IW  = CARD_W - CARD_GAP # inner card width
STAT_HW  = CARD_IW / 2       # half-width for 2-col stats grid

SCHOOL_COLORS = {
    "Evocation":     HexColor("#B03A2E"),
    "Illusion":      HexColor("#7D3C98"),
    "Necromancy":    HexColor("#212F3C"),
    "Conjuration":   HexColor("#117A65"),
    "Enchantment":   HexColor("#B7770D"),
    "Divination":    HexColor("#1F618D"),
    "Transmutation": HexColor("#1E8449"),
    "Abjuration":    HexColor("#707B7C"),
}

TAG_CFG = {
    "C":        ("Concentration",  HexColor("#1F618D")),
    "R":        ("Ritual",         HexColor("#117A65")),
    "prepared": ("PREPARED",       HexColor("#8B6914")),
    "react":    ("REACTION",       HexColor("#7D3C98")),
    "obsolete": ("OBSOLETE",       HexColor("#707B7C")),
}


# ── Page drawing ───────────────────────────────────────────────────────────────
def draw_page(canv, doc):
    canv.saveState()
    canv.setFillColor(PARCHMENT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    for inset, lw in [(6*mm, 1.5), (8.5*mm, 0.5)]:
        canv.setStrokeColor(RULE_COLOR)
        canv.setLineWidth(lw)
        canv.rect(inset, inset, PAGE_W - 2*inset, PAGE_H - 2*inset, fill=0, stroke=1)
    canv.setFillColor(ACCENT)
    canv.rect(9*mm, PAGE_H - 22*mm, PAGE_W - 18*mm, 13*mm, fill=1, stroke=0)
    canv.setFont("Times-BoldItalic", 11)
    canv.setFillColor(PARCHMENT)
    canv.drawString(12*mm, PAGE_H - 14*mm, CHARACTER_NAME)
    canv.setFont("Times-Bold", 11)
    canv.drawRightString(PAGE_W - 12*mm, PAGE_H - 14*mm, "Spellbook")
    canv.setFont("Times-Italic", 7)
    canv.setFillColor(ACCENT)
    canv.drawCentredString(PAGE_W / 2, 10*mm,
        f"{CAMPAIGN}  ·  Spellbook  ·  page {doc.page}")
    canv.restoreState()


# ── Text styles ────────────────────────────────────────────────────────────────
SEC_S      = ParagraphStyle("SS", fontName="Times-Bold",   fontSize=11, textColor=HEADER_FG,
                             backColor=HEADER_BG, alignment=TA_CENTER, borderPad=2*mm,
                             spaceBefore=4*mm, spaceAfter=2*mm)
NAME_S     = ParagraphStyle("CN", fontName="Times-Bold",   fontSize=9,  textColor=HEADER_FG, leading=11)
SUB_S      = ParagraphStyle("CS", fontName="Times-Italic", fontSize=7,  textColor=HEADER_FG, leading=9)
STAT_LBL_S = ParagraphStyle("SL", fontName="Times-Bold",   fontSize=6,  textColor=ACCENT,    leading=7.5)
STAT_VAL_S = ParagraphStyle("SV", fontName="Times-Roman",  fontSize=6.5,textColor=INK_DARK,  leading=8)
BODY_S     = ParagraphStyle("BD", fontName="Times-Roman",  fontSize=7.5,textColor=INK_DARK,  leading=10)
UPCAST_S   = ParagraphStyle("UP", fontName="Times-Italic", fontSize=7,  textColor=ACCENT,    leading=9)
SOURCE_S   = ParagraphStyle("SO", fontName="Times-Italic", fontSize=6.5,textColor=INK_MID,   leading=8)
TAG_S      = ParagraphStyle("TG", fontName="Times-Bold",   fontSize=6,  textColor=HEADER_FG, leading=8,
                             alignment=TA_CENTER)


# ── Spell data ─────────────────────────────────────────────────────────────────
SPELLS = [
    # ── Cantrips ──────────────────────────────────────────────────────────────
    dict(section="Cantrips",
         name="Fire Bolt", school="Evocation", level="Cantrip",
         source="Wizard · Attack +7",
         tags=[],
         casting_time="Action", range="120 ft", components="V, S", duration="Instantaneous",
         desc="Ranged spell attack. Hit: 1d10 fire damage. Ignites unattended flammable objects.",
         upcast="2d10 @ lvl 5 · 3d10 @ lvl 11 · 4d10 @ lvl 17"),

    dict(section="Cantrips",
         name="Poison Spray", school="Necromancy", level="Cantrip",
         source="Wizard",
         tags=[],
         casting_time="Action", range="10 ft", components="V, S", duration="Instantaneous",
         desc="CON save (DC 15) or take 1d12 poison damage. Very short range — be careful.",
         upcast="2d12 @ lvl 5 · 3d12 @ lvl 11 · 4d12 @ lvl 17"),

    dict(section="Cantrips",
         name="True Strike (2024)", school="Evocation", level="Cantrip",
         source="Wizard · Attack +7 (INT)",
         tags=[],
         casting_time="Action", range="Self", components="S", duration="Instantaneous",
         desc="Make a melee or ranged spell attack using INT instead of STR/DEX. Hit: 1d6 + INT (+4) radiant damage. NOT the old 'gain advantage' version.",
         upcast="2d6 @ lvl 5 · 3d6 @ lvl 11 · 4d6 @ lvl 17"),

    dict(section="Cantrips",
         name="Guidance", school="Divination", level="Cantrip",
         source="Acolyte background (Cleric)",
         tags=["C"],
         casting_time="Action", range="Touch", components="V, S", duration="Conc., 1 min",
         desc="One willing creature you touch adds 1d4 to one ability check of their choice before the spell ends.",
         upcast=None),

    dict(section="Cantrips",
         name="Thaumaturgy", school="Transmutation", level="Cantrip",
         source="Acolyte background (Cleric)",
         tags=[],
         casting_time="Action", range="30 ft", components="V", duration="Up to 1 min",
         desc="Minor magical effect: voice 3× louder, flames change colour, harmless tremors, instant sound, doors fly open/shut, or alter eye appearance. Up to 3 effects active at once.",
         upcast=None),

    dict(section="Cantrips",
         name="Minor Illusion", school="Illusion", level="Cantrip",
         source="Wizard · Illusionist (always known)",
         tags=["prepared"],
         # Illusionist: +60 ft to illusion spells with 10+ ft range (30 → 90 ft)
         # Illusionist: no verbal components for illusion spells (already none here)
         # Illusionist: can cast as Bonus Action; creates BOTH sound AND image
         casting_time="Action or Bonus Action", range="90 ft (30+60 Illusionist)",
         components="S, M (fleece)", duration="1 minute",
         desc="Create a SOUND and an IMAGE (5-ft cube) simultaneously — both at once thanks to Improved Minor Illusion. Investigation vs DC 15 to disbelieve on physical interaction. Can be cast as a Bonus Action.",
         upcast=None),

    dict(section="Cantrips",
         name="Toll the Dead", school="Necromancy", level="Cantrip",
         source="Magic Initiate (Cleric)",
         tags=[],
         casting_time="Action", range="60 ft", components="V, S", duration="Instantaneous",
         desc="WIS save (DC 15) or take 1d8 necrotic. If target is MISSING any HP, damage becomes 1d12 instead. Great follow-up cantrip after a hit.",
         upcast="2d8/2d12 @ lvl 5 · 3d8/3d12 @ lvl 11 · 4d8/4d12 @ lvl 17"),

    dict(section="Cantrips",
         name="Starry Wisp", school="Evocation", level="Cantrip",
         source="Magic Initiate (Cleric) · Attack +7",
         tags=[],
         casting_time="Action", range="60 ft", components="V, S", duration="Instantaneous",
         desc="Ranged spell attack. Hit: 1d8 radiant. Target emits dim light 10 ft and cannot benefit from Invisible until start of your next turn.",
         upcast="2d8 @ lvl 5 · 3d8 @ lvl 11 · 4d8 @ lvl 17"),

    # ── Level 1 ───────────────────────────────────────────────────────────────
    dict(section="Level 1 Spells",
         name="Command", school="Enchantment", level="1st Level",
         source="Acolyte (Cleric) · 1st-level slot",
         tags=[],
         casting_time="Action", range="60 ft", components="V", duration="1 round",
         desc="WIS save (DC 15) or obey one-word command next turn. Examples: Approach, Drop, Flee, Grovel, Halt. No effect on Undead or creatures that don't understand you.",
         upcast="+1 extra target per slot level above 1st"),

    dict(section="Level 1 Spells",
         name="Magic Missile", school="Evocation", level="1st Level",
         source="Wizard · 1st-level slot",
         tags=[],
         casting_time="Action", range="120 ft", components="V, S", duration="Instantaneous",
         desc="3 darts of magical force, each dealing 1d4+1 force damage. AUTO-HIT — no attack roll needed. Split between any number of targets freely.",
         upcast="+1 dart per slot level above 1st (4 @ 2nd · 5 @ 3rd…)"),

    dict(section="Level 1 Spells",
         name="Mage Armor", school="Abjuration", level="1st Level",
         source="Wizard · superseded by Scale Mail",
         tags=["obsolete"],
         casting_time="Action", range="Touch", components="V, S, M (leather)", duration="8 hours",
         desc="Target AC = 13 + DEX modifier if wearing no armour. OBSOLETE: Scale Mail gives AC 16 vs Mage Armor AC 15. Still in spellbook but not prepared.",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Grease", school="Conjuration", level="1st Level",
         source="Magic Initiate (Cleric) · 1st-level slot",
         tags=[],
         casting_time="Action", range="60 ft", components="V, S, M (butter)", duration="1 minute",
         desc="10-ft square becomes difficult terrain for 1 min. On cast: DEX save (DC 15) or Prone. Same save when entering or ending a turn in the grease. Great vs ogres!",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Unseen Servant", school="Conjuration", level="1st Level",
         source="Wizard · Ritual — no slot needed",
         tags=["R"],
         casting_time="Action / Ritual +10 min", range="60 ft",
         components="V, S, M (string)", duration="1 hour",
         desc="Invisible mindless force (STR 2, AC 10, 1 HP). Bonus Action: move 15 ft and interact with an object. Carries up to 25 lbs. Cannot attack.",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Find Familiar", school="Conjuration", level="1st Level",
         source="Wizard · Ritual — no slot needed",
         tags=["R"],
         casting_time="1 hour ritual", range="10 ft",
         components="V, S, M (10 gp consumed)", duration="Until dismissed",
         desc="Spirit in animal form (bat, cat, hawk, owl, raven, etc.). Share its senses (Action). Deliver touch spells through it within 100 ft. Reappears at 0 HP with recasting.",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Comprehend Languages", school="Divination", level="1st Level",
         source="Wizard · Ritual — no slot needed",
         tags=["R"],
         casting_time="Action / Ritual +10 min", range="Self",
         components="V, S, M (soot, salt)", duration="1 hour",
         desc="Understand any spoken language you hear and any written language you touch (1 min/page). Does NOT grant ability to speak or write the language.",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Tenser's Floating Disk", school="Conjuration", level="1st Level",
         source="Wizard · Ritual — no slot needed",
         tags=["R"],
         casting_time="Action / Ritual +10 min", range="30 ft",
         components="V, S, M (mercury drop)", duration="1 hour",
         desc="3-ft wide disc of force hovering 1 ft off ground. Carries up to 500 lbs. Follows you within 20 ft automatically. Vanishes if more than 100 ft away.",
         upcast=None),

    dict(section="Level 1 Spells",
         name="Silent Image", school="Illusion", level="1st Level (2nd slot)",
         source="Wizard · costs 2nd-level slot",
         tags=["C"],
         # Illusionist: no verbal; range 60 ft → 120 ft (+60)
         casting_time="Action", range="120 ft (60+60 Illusionist)",
         components="S, M (fleece)", duration="Conc., 10 min",
         desc="Create a 15-ft cube visual illusion (no sound, smell, or texture). Investigation vs DC 15 to disbelieve on physical interaction. Action: move image. No verbal needed (Illusionist).",
         upcast="Requires 2nd-level slot"),

    dict(section="Level 1 Spells",
         name="Silvery Barbs", school="Enchantment", level="1st Level (2nd slot)",
         source="Wizard · costs 2nd-level slot",
         tags=["react"],
         casting_time="Reaction", range="60 ft",
         components="V", duration="Instantaneous",
         desc="Trigger: creature within 60 ft succeeds on attack roll, ability check, or save. Force them to reroll, taking the lower result. Then choose a different creature — it gains advantage on its next d20 roll.",
         upcast="Requires 2nd-level slot"),

    dict(section="Level 1 Spells",
         name="Color Spray", school="Illusion", level="1st Level",
         source="Wizard · any slot",
         tags=["prepared"],
         # Illusionist: no verbal. Range is Self so no +60 ft.
         casting_time="Action", range="Self (15-ft cone)",
         components="S, M (sand/powder)", duration="1 round",
         desc="Roll 6d10 — that many HP worth of creatures in the cone (lowest HP first) are Blinded for 1 round. Undead and creatures immune to being blinded are unaffected.",
         upcast="+2d10 HP worth per slot level above 1st"),

    # ── Level 2 ───────────────────────────────────────────────────────────────
    dict(section="Level 2 Spells",
         name="Magic Weapon", school="Transmutation", level="2nd Level (3rd slot)",
         source="Wizard · costs 3rd-level slot",
         tags=["C"],
         casting_time="Bonus Action", range="Touch",
         components="V, S", duration="Conc., 1 hour",
         desc="A nonmagical weapon becomes +1 magic weapon. Bypasses resistance and immunity to nonmagical attacks — crucial against constructs and undead.",
         upcast="+2 bonus @ 4th slot · +3 bonus @ 6th slot. Requires 3rd-level slot."),

    dict(section="Level 2 Spells",
         name="Nystul's Magic Aura", school="Illusion", level="2nd Level",
         source="Wizard (Illusionist) · 2nd-level slot",
         tags=[],
         # Illusionist: no verbal. Touch range < 10 ft so no range bonus.
         casting_time="Action", range="Touch",
         components="S, M (silk square)", duration="24 hours",
         desc="False Aura: make a target appear magical/nonmagical or a different school. Mask: change apparent creature type for divination spells. Cast daily for 30 days = permanent.",
         upcast=None),

    dict(section="Level 2 Spells",
         name="Invisibility", school="Illusion", level="2nd Level",
         source="Wizard (Illusionist) · 2nd-level slot",
         tags=["C", "prepared"],
         # Illusionist: no verbal. Touch range < 10 ft so no range bonus.
         casting_time="Action", range="Touch",
         components="S, M (eyelash in gum arabic)", duration="Conc., 1 hour",
         desc="Target becomes Invisible (everything worn/carried too). Ends immediately if target makes an attack roll, deals damage, or casts a spell.",
         upcast="+1 additional target per slot above 2nd"),


    # ── Ranger ────────────────────────────────────────────────────────────────
    dict(section="Ranger Spells",
         name="Hunter's Mark", school="Divination", level="1st Level · Ranger",
         source="Ranger · WIS DC 11 · 2×/day FREE (Favored Enemy)",
         tags=["C", "prepared"],
         casting_time="Bonus Action", range="90 ft",
         components="V", duration="Conc., 1 hour",
         desc="Mark a creature. Deal extra 1d6 damage to it on every hit. If it dies, Bonus Action to move mark. FAVORED ENEMY (Hobgoblin): cast 2× per day FREE without a spell slot.",
         upcast="3rd slot: Conc. up to 8 hr · 5th slot: Conc. up to 24 hr"),

    dict(section="Ranger Spells",
         name="Cure Wounds", school="Abjuration", level="1st Level · Ranger",
         source="Ranger · WIS DC 11 · 1st-level slot",
         tags=["prepared"],
         casting_time="Action", range="Touch",
         components="V, S", duration="Instantaneous",
         desc="A creature you touch regains 2d8 + WIS modifier HP. Has no effect on Undead or Constructs.",
         upcast="+2d8 per slot level above 1st (4d8+WIS @ 2nd · 6d8+WIS @ 3rd…)"),
]


# ── Card builder ───────────────────────────────────────────────────────────────
def build_card(spell):
    sc = SCHOOL_COLORS.get(spell["school"], ACCENT)
    iw = CARD_IW

    data   = []
    styles = [
        ("BOX",           (0, 0), (-1, -1), 0.8, RULE_COLOR),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]

    def r():
        return len(data) - 1

    # Row: Name
    data.append([Paragraph(spell["name"], NAME_S)])
    styles += [("BACKGROUND", (0, r()), (0, r()), sc),
               ("TOPPADDING",    (0, r()), (0, r()), 4),
               ("BOTTOMPADDING", (0, r()), (0, r()), 1)]

    # Row: Sublabel
    data.append([Paragraph(f"{spell['school']} · {spell['level']}", SUB_S)])
    styles += [("BACKGROUND",    (0, r()), (0, r()), sc),
               ("TOPPADDING",    (0, r()), (0, r()), 0),
               ("BOTTOMPADDING", (0, r()), (0, r()), 4)]

    # Row: Tags (optional — zero-padding row wrapping a mini table)
    tags = [t for t in spell.get("tags", []) if t in TAG_CFG]
    if tags:
        n  = len(tags)
        tw = iw / n
        tag_tbl = Table(
            [[Paragraph(TAG_CFG[t][0], TAG_S) for t in tags]],
            colWidths=[tw] * n,
        )
        ts = [("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2),
              ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2),
              ("ALIGN", (0,0), (-1,-1), "CENTER")]
        for i, t in enumerate(tags):
            ts.append(("BACKGROUND", (i, 0), (i, 0), TAG_CFG[t][1]))
        tag_tbl.setStyle(TableStyle(ts))
        data.append([tag_tbl])
        styles += [("LEFTPADDING",   (0, r()), (0, r()), 0),
                   ("RIGHTPADDING",  (0, r()), (0, r()), 0),
                   ("TOPPADDING",    (0, r()), (0, r()), 0),
                   ("BOTTOMPADDING", (0, r()), (0, r()), 0)]

    # Row: Stats 2×2 grid (casting time, range, components, duration)
    hw = iw / 2
    stat_tbl = Table(
        [
            [Paragraph("Casting Time", STAT_LBL_S), Paragraph("Range", STAT_LBL_S)],
            [Paragraph(spell["casting_time"], STAT_VAL_S), Paragraph(spell["range"], STAT_VAL_S)],
            [Paragraph("Components", STAT_LBL_S), Paragraph("Duration", STAT_LBL_S)],
            [Paragraph(spell["components"], STAT_VAL_S), Paragraph(spell["duration"], STAT_VAL_S)],
        ],
        colWidths=[hw, hw],
    )
    stat_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), SHADE_ROW),
        ("LINEAFTER",     (0, 0), (0, -1),  0.3, RULE_COLOR),
        ("LINEBELOW",     (0, 1), (-1,  1), 0.3, RULE_COLOR),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))
    data.append([stat_tbl])
    styles += [("LEFTPADDING",   (0, r()), (0, r()), 0),
               ("RIGHTPADDING",  (0, r()), (0, r()), 0),
               ("TOPPADDING",    (0, r()), (0, r()), 0),
               ("BOTTOMPADDING", (0, r()), (0, r()), 0)]

    # Row: Description
    data.append([Paragraph(spell["desc"], BODY_S)])
    styles += [("BACKGROUND", (0, r()), (0, r()), PARCHMENT),
               ("TOPPADDING",    (0, r()), (0, r()), 4),
               ("BOTTOMPADDING", (0, r()), (0, r()), 3)]

    # Row: Upcast (optional)
    if spell.get("upcast"):
        data.append([Paragraph(f"↑ {spell['upcast']}", UPCAST_S)])
        styles += [("BACKGROUND", (0, r()), (0, r()), SHADE_ROW),
                   ("TOPPADDING",    (0, r()), (0, r()), 2),
                   ("BOTTOMPADDING", (0, r()), (0, r()), 2)]

    # Row: Source footer
    data.append([Paragraph(spell.get("source", ""), SOURCE_S)])
    styles += [("BACKGROUND",    (0, r()), (0, r()), FOOTER_BG),
               ("TOPPADDING",    (0, r()), (0, r()), 2),
               ("BOTTOMPADDING", (0, r()), (0, r()), 3)]

    return Table(data, colWidths=[iw], style=TableStyle(styles))


def spell_row(left, right=None):
    lc = build_card(left)
    rc = build_card(right) if right else Spacer(CARD_W, 1)
    row = Table([[lc, rc]], colWidths=[CARD_W, CARD_W])
    row.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        # gap between cards: right-pad the left cell
        ("RIGHTPADDING",  (0, 0), (0,  0), CARD_GAP),
    ]))
    return row


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    OUTPUT = "Tiberius-Spellbook.pdf"

    doc = BaseDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=LMARGIN, rightMargin=RMARGIN,
        topMargin=TMARGIN, bottomMargin=BMARGIN,
    )
    frame = Frame(LMARGIN, BMARGIN, CONTENT_W, CONTENT_H,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_page)])

    story = [Spacer(1, 2 * mm)]

    sections = ["Cantrips", "Level 1 Spells", "Level 2 Spells", "Ranger Spells"]
    for section in sections:
        spells = [s for s in SPELLS if s["section"] == section]
        if not spells:
            continue
        story.append(Paragraph(section, SEC_S))
        for i in range(0, len(spells), 2):
            story.append(spell_row(spells[i], spells[i + 1] if i + 1 < len(spells) else None))

    doc.build(story)
    size = os.path.getsize(OUTPUT)
    print(f"✓  {OUTPUT}  ({size // 1024} KB)")


if __name__ == "__main__":
    main()
