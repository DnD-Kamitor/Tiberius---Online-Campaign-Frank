"""
Tiberius Goodbook Ledger Generator  v2
Uses BaseDocTemplate + named PageTemplates so every page (including overflow)
carries the correct section title.
Run:  .venv/bin/python generate_ledger.py
Out:  Tiberius-Ledger.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Table, TableStyle, Paragraph, Spacer,
    PageBreak, NextPageTemplate,
)

# ── Palette ───────────────────────────────────────────────────────────────────
PARCHMENT  = HexColor("#F5EDD6")
INK_DARK   = HexColor("#1A1008")
INK_MID    = HexColor("#3D2B0F")
RULE_COLOR = HexColor("#8B6914")
ACCENT     = HexColor("#5C3A1E")
HEADER_BG  = HexColor("#3D2B0F")
HEADER_FG  = HexColor("#F5EDD6")
SHADE_ROW  = HexColor("#EDE3C8")

PAGE_W, PAGE_H = A4
LMARGIN = RMARGIN = 12 * mm
TMARGIN = 26 * mm
BMARGIN = 16 * mm
CONTENT_W = PAGE_W - LMARGIN - RMARGIN
CONTENT_H = PAGE_H - TMARGIN - BMARGIN

CHARACTER_NAME = "Tiberius Inscriptus Interlinearis"
CAMPAIGN       = "Frank's Campaign"

# ── Per-page background ───────────────────────────────────────────────────────
def draw_page(canv, doc, title):
    canv.saveState()
    canv.setFillColor(PARCHMENT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    for inset, lw in [(6*mm, 1.5), (8.5*mm, 0.5)]:
        canv.setStrokeColor(RULE_COLOR)
        canv.setLineWidth(lw)
        canv.rect(inset, inset, PAGE_W - 2*inset, PAGE_H - 2*inset,
                  fill=0, stroke=1)
    canv.setFillColor(ACCENT)
    canv.rect(9*mm, PAGE_H - 22*mm, PAGE_W - 18*mm, 13*mm, fill=1, stroke=0)
    canv.setFont("Times-BoldItalic", 11)
    canv.setFillColor(PARCHMENT)
    canv.drawString(12*mm, PAGE_H - 14*mm, CHARACTER_NAME)
    canv.setFont("Times-Bold", 11)
    canv.drawRightString(PAGE_W - 12*mm, PAGE_H - 14*mm, title)
    canv.setFont("Times-Italic", 7)
    canv.setFillColor(ACCENT)
    canv.drawCentredString(PAGE_W / 2, 10*mm,
        f"{CAMPAIGN}  ·  The Goodbook  ·  page {doc.page}")
    canv.restoreState()


def make_template(tid, title):
    frame = Frame(LMARGIN, BMARGIN, CONTENT_W, CONTENT_H,
                  leftPadding=0, rightPadding=0,
                  topPadding=0,  bottomPadding=0)
    return PageTemplate(id=tid, frames=[frame],
                        onPage=lambda c, d, t=title: draw_page(c, d, t))


# ── Table style helpers ───────────────────────────────────────────────────────
def tbl_style(nheader=1, nrows=0, shade=True, extra=()):
    cmds = [
        ("BACKGROUND",    (0, 0), (-1, nheader-1), HEADER_BG),
        ("TEXTCOLOR",     (0, 0), (-1, nheader-1), HEADER_FG),
        ("FONTNAME",      (0, 0), (-1, nheader-1), "Times-Bold"),
        ("FONTSIZE",      (0, 0), (-1, nheader-1), 8),
        ("ALIGN",         (0, 0), (-1, nheader-1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1),         "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1),          0.4, RULE_COLOR),
        ("LINEBELOW",     (0, nheader-1), (-1, nheader-1), 1.0, RULE_COLOR),
        ("FONTNAME",      (0, nheader), (-1, -1), "Times-Roman"),
        ("FONTSIZE",      (0, nheader), (-1, -1), 8),
        ("TEXTCOLOR",     (0, nheader), (-1, -1), INK_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]
    if shade:
        for r in range(nheader, nrows, 2):
            cmds.append(("BACKGROUND", (0, r), (-1, r), SHADE_ROW))
    cmds.extend(extra)
    return TableStyle(cmds)


def blank(n, cols):
    return [[""] * cols for _ in range(n)]


# ── Text styles ───────────────────────────────────────────────────────────────
H1 = ParagraphStyle("H1", fontName="Times-Bold", fontSize=13,
                    textColor=INK_MID, spaceAfter=2*mm, alignment=TA_CENTER)
H2 = ParagraphStyle("H2", fontName="Times-Bold", fontSize=10,
                    textColor=ACCENT, spaceBefore=3*mm, spaceAfter=1.5*mm)
NOTE = ParagraphStyle("Note", fontName="Times-Italic", fontSize=7.5,
                      textColor=ACCENT, spaceAfter=2*mm)


# ── Page builders ─────────────────────────────────────────────────────────────

def page_treasury(s):
    s += [Spacer(1, 4*mm),
          Paragraph("Treasury Ledger", H1),
          Paragraph(
              "Record every transaction. "
              "<b>Out</b> = gold leaving your hands.  "
              "<b>In</b> = gold arriving.  "
              "Keep a running GP balance in the last column.", NOTE)]

    # Current balances
    bal = [
        ["CURRENT BALANCES", "", "", "", "", ""],
        ["Location",              "CP",  "SP", "EP", "GP",             "PP"],
        ["On Person",             "202", "69", "",   "586",            ""],
        ["Electrum (22 x 0.5)",   "",    "",   "22", "11 GP equiv.",   ""],
        ["Banked",                "",    "",   "",   "450",            ""],
        ["Treasure (Silver Urn)", "",    "",   "",   "? (unappraised)",""],
        ["TOTAL (est. GP)",       "",    "",   "",   "~1,058",         ""],
    ]
    cw6 = [CONTENT_W * f for f in (0.22, 0.10, 0.10, 0.10, 0.28, 0.20)]
    bt = Table(bal, colWidths=cw6)
    bt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0), (-1,0),  HEADER_FG),
        ("SPAN",          (0,0), (-1,0)),
        ("ALIGN",         (0,0), (-1,0),  "CENTER"),
        ("FONTNAME",      (0,0), (-1,0),  "Times-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("BACKGROUND",    (0,1), (-1,1),  HEADER_BG),
        ("TEXTCOLOR",     (0,1), (-1,1),  HEADER_FG),
        ("FONTNAME",      (0,1), (-1,1),  "Times-Bold"),
        ("FONTSIZE",      (0,1), (-1,1),  8),
        ("ALIGN",         (1,1), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.5, RULE_COLOR),
        ("FONTNAME",      (0,2), (-1,-1), "Times-Roman"),
        ("FONTSIZE",      (0,2), (-1,-1), 8),
        ("TEXTCOLOR",     (0,2), (-1,-1), INK_DARK),
        ("BACKGROUND",    (0,6), (-1,6),  SHADE_ROW),
        ("FONTNAME",      (0,6), (-1,6),  "Times-Bold"),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 3),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3),
    ]))
    s += [bt, Spacer(1, 4*mm)]

    # Transaction log — wide columns, repeating header
    s.append(Paragraph("Transaction Log", H2))
    cw_tx = [CONTENT_W * f for f in (0.06, 0.10, 0.08, 0.30, 0.11, 0.11, 0.10, 0.14)]
    head = [["Sess.", "Date", "Type", "Description / Source",
             "Out (GP)", "In (GP)", "Net", "Balance"]]
    pre = [
        # ── Session 0: starting treasury ──────────────────────────────────────
        ["0", "2026-05-22", "Open",
         "Opening balance — party treasury (7000+3900+450 banked)",
         "", "11,350", "+11,350", "11,350"],
        ["0", "2026-05-22", "Buy",
         "Gloves of Thievery — Jakhad (rogue)",
         "600", "", "−600", "10,750"],
        ["0", "2026-05-22", "Buy",
         "Javelin of Lightning — Tiberius",
         "600", "", "−600", "10,150"],
        ["0", "2026-05-22", "Buy",
         "Mind Sharpener — Tela (druid)",
         "600", "", "−600", "9,550"],
        ["0", "2026-05-22", "Buy",
         "Mind Sharpener (ring) — Aella (cleric)",
         "600", "", "−600", "8,950"],
        ["0", "2026-05-22", "Buy",
         "2x Potion of Healing — party stock",
         "200", "", "−200", "8,750"],
        ["0", "2026-05-22", "Buy",
         "Adventuring supplies: lighting, exploration, writing & tactical kits",
         "21", "", "−21", "8,729"],
    ]
    data = head + pre + blank(23, 8)
    t = Table(data, colWidths=cw_tx, repeatRows=1)
    t.setStyle(tbl_style(1, len(data), extra=[
        ("ALIGN", (4,1), (-1,-1), "RIGHT"),
        ("ALIGN", (0,1), (2,-1), "CENTER"),
    ]))
    s += [t, Spacer(1, 2*mm),
          Paragraph("CP=copper  SP=silver  EP=electrum (1/2 GP)  GP=gold  PP=platinum (10 GP)", NOTE)]


def page_spells(s):
    s += [Spacer(1, 4*mm),
          Paragraph("Spell Usage Journal", H1),
          Paragraph(
              "Log every spell cast. Tick slot boxes as you expend them each session; "
              "erase or re-print at each long rest.", NOTE),
          Paragraph("Spell Slot Tracker", H2)]

    # Slot tracker — boxes as "[ ]" text
    def slots(n): return "  ".join(["[ ]"] * n)
    slot_data = [
        ["Level", "Max / Session", "Slots (mark X when used — reset on long rest)"],
        ["1st",   "4",  slots(4)],
        ["2nd",   "2",  slots(2)],
        ["3rd",   "—",  slots(3) + "      (future)"],
        ["4th",   "—",  slots(3) + "      (future)"],
        ["5th+",  "—",  slots(3) + "      (future)"],
    ]
    cw_sl = [CONTENT_W * f for f in (0.08, 0.13, 0.79)]
    st = Table(slot_data, colWidths=cw_sl)
    st.setStyle(tbl_style(1, len(slot_data)))
    s += [st, Spacer(1, 4*mm),
          Paragraph("Cast Log", H2)]

    cw_sp = [CONTENT_W * f for f in (0.06, 0.10, 0.24, 0.09, 0.09, 0.16, 0.26)]
    head_sp = [["Sess.", "Date", "Spell Name", "Lvl Cast", "Slot Used",
                "Target / Area", "Notes / Outcome"]]
    data_sp = head_sp + blank(32, 7)
    t = Table(data_sp, colWidths=cw_sp, repeatRows=1)
    t.setStyle(tbl_style(1, len(data_sp), extra=[
        ("ALIGN", (0,1), (4,-1), "CENTER"),
    ]))
    s += [t, Spacer(1, 2*mm),
          Paragraph("Cantrips use no slots but are still worth logging for session review.", NOTE)]


def page_items(s):
    s += [Spacer(1, 4*mm),
          Paragraph("Item Acquisitions Log", H1),
          Paragraph(
              "Every item that enters or leaves Tiberius's hands.  "
              "Status key:  <b>K</b>=Kept  <b>S</b>=Sold  <b>U</b>=Used/Consumed  "
              "<b>G</b>=Given away  <b>L</b>=Lost/Stolen", NOTE)]

    # Starting inventory snapshot
    s.append(Paragraph("Starting Inventory Snapshot — Level 3", H2))
    inv = [
        ["#", "Item",                    "Qty", "Source",       "Est. Value", "Status", "Notes"],
        ["1",  "Light Crossbow",         "1",   "Starting",     "25 GP",      "K", ""],
        ["2",  "Quarterstaff",           "1",   "Starting",     "2 SP",       "K", "Versatile 1d8"],
        ["3",  "Golden Neck with Blood", "1",   "Found",        "unknown",    "K", "Equipment slot"],
        ["4",  "Scholar's Pack",         "1",   "Starting",     "40 GP",      "K", "Backpack + contents"],
        ["5",  "Book",                   "1",   "Pack",         "25 GP",      "K", ""],
        ["6",  "Ink (1 oz.)",            "1",   "Pack",         "10 GP",      "K", ""],
        ["7",  "Ink Pen",                "1",   "Pack",         "2 CP",       "K", ""],
        ["8",  "Lamp",                   "1",   "Pack",         "5 SP",       "K", ""],
        ["9",  "Oil (flask)",           "10",   "Pack",         "1 GP ea",    "K", ""],
        ["10", "Parchment (sheet)",     "10",   "Pack",         "1 GP ea",    "K", ""],
        ["11", "Tinderbox",              "1",   "Pack",         "5 SP",       "K", ""],
        ["12", "Silver Urn",             "1",   "Treasure",     "? GP",       "K", "Unappraised"],
    ]
    cw_inv = [CONTENT_W * f for f in (0.05, 0.26, 0.06, 0.12, 0.11, 0.09, 0.31)]
    t_inv = Table(inv, colWidths=cw_inv)
    t_inv.setStyle(tbl_style(1, len(inv), extra=[
        ("ALIGN", (0,0), (2,-1), "CENTER"),
        ("ALIGN", (5,0), (5,-1), "CENTER"),
    ]))
    s += [t_inv, Spacer(1, 4*mm)]

    # Acquisitions log
    s.append(Paragraph("Acquisitions & Changes Log", H2))
    cw_acq = [CONTENT_W * f for f in (0.06, 0.10, 0.25, 0.07, 0.15, 0.12, 0.07, 0.18)]
    head_acq = [["Sess.", "Date", "Item Name", "Qty", "Source / How",
                 "Value (GP)", "Status", "Notes"]]
    data_acq = head_acq + blank(24, 8)
    t_acq = Table(data_acq, colWidths=cw_acq, repeatRows=1)
    t_acq.setStyle(tbl_style(1, len(data_acq), extra=[
        ("ALIGN", (0,1), (1,-1), "CENTER"),
        ("ALIGN", (3,1), (3,-1), "CENTER"),
        ("ALIGN", (6,1), (6,-1), "CENTER"),
    ]))
    s += [t_acq, Spacer(1, 4*mm)]

    # Magic items
    s.append(Paragraph("Magic Items & Attunement  (max 3 attuned simultaneously)", H2))
    mag = [
        ["Slot", "Item Name",                   "Attuned?", "Session Found", "Properties / Notes"],
        ["1",    "Javelin of Lightning",          "[ ]",      "Sess. 0",
         "Throw + speak command word: 5ft wide 120ft line, DC13 DEX or 4d6 lightning; "
         "1/dawn. Uncommon weapon."],
        ["2",    "",                             "[ ]",      "",              ""],
        ["3",    "",                             "[ ]",      "",              "(attunement slots above)"],
        ["4",    "",                             "",         "",              ""],
        ["5",    "",                             "",         "",              ""],
    ]
    cw_mag = [CONTENT_W * f for f in (0.07, 0.27, 0.12, 0.14, 0.40)]
    t_mag = Table(mag, colWidths=cw_mag)
    t_mag.setStyle(tbl_style(1, len(mag), extra=[
        ("ALIGN", (0,0), (2,-1), "CENTER"),
    ]))
    s.append(t_mag)


def page_milestones(s):
    s += [Spacer(1, 4*mm),
          Paragraph("Milestones & Level-up Log", H1),
          Paragraph(
              "Track XP, level transitions, feat/ASI choices, and notable session events.", NOTE)]

    # Level progression
    s.append(Paragraph("Level Progression Table", H2))
    lvl = [
        ["Lvl", "XP Needed", "Date",  "New Features / ASI / Feats",                          "Spell Slots",        "New Spells"],
        ["1",   "0",          "",      "Spellcasting, Arcane Recovery, Illusionist subclass",  "1st x2",            ""],
        ["2",   "300",        "",      "Spellbook growth (+2)",                                "1st x3",            ""],
        ["3",   "900",        "NOW",   "2nd-level slots; Improved Minor Illusion (subclass)",  "1st x4  2nd x2",    ""],
        ["4",   "2700",       "",      "ASI or Feat",                                          "1st x4  2nd x3",    ""],
        ["5",   "6500",       "",      "3rd-level slots",                                      "1st x4  2nd x3  3rd x2", ""],
        ["6",   "14000",      "",      "Malleable Illusions (subclass)",                       "...",               ""],
        ["7",   "23000",      "",      "",                                                     "...",               ""],
        ["8",   "34000",      "",      "ASI or Feat",                                          "...",               ""],
        ["9",   "48000",      "",      "5th-level slots",                                      "...",               ""],
        ["10",  "64000",      "",      "Illusory Self (subclass)",                             "...",               ""],
        ["11",  "85000",      "",      "6th-level slots",                                      "...",               ""],
        ["12",  "100000",     "",      "ASI or Feat",                                          "...",               ""],
    ]
    cw_lvl = [CONTENT_W * f for f in (0.06, 0.10, 0.10, 0.36, 0.21, 0.17)]
    t_lvl = Table(lvl, colWidths=cw_lvl)
    t_lvl.setStyle(tbl_style(1, len(lvl), extra=[
        # Highlight level 3 (current)
        ("BACKGROUND", (0,3), (-1,3), HexColor("#D4E8D4")),
        ("FONTNAME",   (0,3), (-1,3), "Times-Bold"),
        ("ALIGN",      (0,0), (2,-1), "CENTER"),
    ]))
    s += [t_lvl, Spacer(1, 4*mm)]

    # Session log
    s.append(Paragraph("Session Milestone Log", H2))
    cw_ms = [CONTENT_W * f for f in (0.07, 0.12, 0.12, 0.12, 0.57)]
    head_ms = [["Sess.", "Date", "XP Earned", "Total XP", "Key Events / Decisions / Notes"]]
    data_ms = head_ms + blank(22, 5)
    t_ms = Table(data_ms, colWidths=cw_ms, repeatRows=1)
    t_ms.setStyle(tbl_style(1, len(data_ms), extra=[
        ("ALIGN", (0,1), (3,-1), "CENTER"),
    ]))
    s += [t_ms, Spacer(1, 4*mm)]

    # Death saves
    s.append(Paragraph("Death Save History", H2))
    cw_ds = [CONTENT_W * f for f in (0.07, 0.12, 0.31, 0.12, 0.12, 0.26)]
    ds = [["Sess.", "Date", "Cause / Enemy", "Successes", "Failures", "Outcome"]]
    ds += blank(8, 6)
    t_ds = Table(ds, colWidths=cw_ds)
    t_ds.setStyle(tbl_style(1, len(ds), extra=[
        ("ALIGN", (0,1), (1,-1), "CENTER"),
        ("ALIGN", (3,1), (4,-1), "CENTER"),
    ]))
    s.append(t_ds)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    OUTPUT = "Tiberius-Ledger.pdf"

    doc = BaseDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=LMARGIN, rightMargin=RMARGIN,
        topMargin=TMARGIN,  bottomMargin=BMARGIN,
    )
    doc.addPageTemplates([
        make_template("treasury",   "Treasury Ledger"),
        make_template("spells",     "Spell Usage Journal"),
        make_template("items",      "Item Acquisitions Log"),
        make_template("milestones", "Milestones & Level-up Log"),
    ])

    story = []

    page_treasury(story)

    story += [NextPageTemplate("spells"), PageBreak()]
    page_spells(story)

    story += [NextPageTemplate("items"), PageBreak()]
    page_items(story)

    story += [NextPageTemplate("milestones"), PageBreak()]
    page_milestones(story)

    doc.build(story)

    import os
    size = os.path.getsize(OUTPUT)
    print(f"✓  {OUTPUT}  ({size // 1024} KB)")


if __name__ == "__main__":
    main()
