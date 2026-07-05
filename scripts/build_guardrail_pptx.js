const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.33, height: 7.5 });
p.layout = "W";
const KR = "Apple SD Gothic Neo", EN = "Calibri";
const s = p.addSlide();
s.background = { color: "FFFFFF" };

// Title
s.addText("H1 and H2 Tradeoff - Physical AI Actions", {
  x: 0.4, y: 0.28, w: 12.53, h: 0.7, align: "center",
  fontFace: EN, fontSize: 24, bold: true, color: "111111",
});

// grid geometry (contiguous 2x2, no gaps)
const gx = 2.55, gy = 1.45, cw = 4.85, ch = 2.25, gpx = 0, gpy = 0;
const cell = (col, row) => ({ x: gx + col * (cw + gpx), y: gy + row * (ch + gpy), w: cw, h: ch });

function quad(col, row, fill, hEN, hKR, note) {
  const c = cell(col, row);
  s.addShape(p.ShapeType.rect, { ...c, fill: { color: fill }, line: { color: "9A9A9A", width: 1 } });
  const runs = [
    { text: hEN, options: { fontFace: EN, fontSize: 17, bold: true, color: "111111", breakLine: true } },
    { text: hKR, options: { fontFace: KR, fontSize: 12.5, color: "7A7A7A", breakLine: true } },
    { text: " ", options: { fontSize: 8, breakLine: true } },
    { text: note, options: { fontFace: EN, fontSize: 11, color: "7A7A7A", breakLine: true } },
  ];
  s.addText(runs, { ...c, align: "center", valign: "middle", margin: 4, lineSpacingMultiple: 1.12 });
}

quad(0, 0, "EDEDED", "Safe · Inefficient", "(안전하나 비효율적)", "Low operational value");
quad(1, 0, "FFFFFF", "Efficient · Safe", "(효율적이고 안전한)", "Desired region");
quad(0, 1, "C4CAD6", "Unsafe · Inefficient", "(위험하고 비효율적)", "Worst on both axes");
quad(1, 1, "EDEDED", "Efficient · Unsafe", "(효율적이나 위험한)", "Highest physical-harm risk");

// left axis pole labels (bold black)
s.addText("Safe", { x: 1.35, y: gy, w: 1.05, h: ch, align: "right", valign: "middle", fontFace: EN, fontSize: 14, bold: true, color: "111111" });
s.addText("Unsafe", { x: 1.25, y: gy + ch + gpy, w: 1.15, h: ch, align: "right", valign: "middle", fontFace: EN, fontSize: 14, bold: true, color: "111111" });
// left axis title (rotated)
s.addText("H1: Safety", { x: -1.35, y: 3.45, w: 4.3, h: 0.5, align: "center", valign: "middle", rotate: 270, fontFace: EN, fontSize: 15, bold: true, color: "111111" });

// bottom axis pole labels
const by = gy + 2 * ch + gpy + 0.08;
s.addText("Inefficient", { x: gx, y: by, w: cw, h: 0.4, align: "center", fontFace: EN, fontSize: 14, bold: true, color: "111111" });
s.addText("Efficient", { x: gx + cw + gpx, y: by, w: cw, h: 0.4, align: "center", fontFace: EN, fontSize: 14, bold: true, color: "111111" });
// bottom axis title
s.addText("H2: Task Efficiency  ( ↓ time, ↓ energy )", { x: gx, y: by + 0.5, w: 2 * cw + gpx, h: 0.4, align: "center", fontFace: EN, fontSize: 15, bold: true, color: "111111" });

p.writeFile({ fileName: "/sessions/gallant-lucid-darwin/mnt/outputs/guardrail_matrix.pptx" }).then(f => console.log("saved", f));
