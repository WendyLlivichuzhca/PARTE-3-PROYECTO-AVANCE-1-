from datetime import datetime
from pathlib import Path


def _escape(text):
    """Escapa caracteres especiales para el stream PDF."""
    return (
        text.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
    )


def _cx(text, size, page_w=595, factor=0.52):
    """Calcula la X para centrar texto con fuente Helvetica."""
    return max(55, (page_w - len(text) * size * factor) / 2)


def generate_certificate(student_name, course_name, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    safe_student = student_name.replace(" ", "_")
    safe_course  = course_name.replace(" ", "_")
    file_path    = output_path / f"certificado_{safe_student}_{safe_course}.pdf"

    date_str = datetime.now().strftime("%d/%m/%Y")

    ops = []

    # ── Bordes dobles del certificado ──────────────────────────
    ops += [
        "q",
        "1.8 w",
        "25 25 545 792 re S",   # borde exterior
        "0.6 w",
        "40 40 515 762 re S",   # borde interior
        "Q",
    ]

    # ── Barra decorativa superior ───────────────────────────────
    ops += [
        "q",
        "0.15 0.35 0.60 rg",    # azul corporativo
        "40 790 515 17 re f",
        "Q",
    ]

    # ── Barra decorativa inferior ───────────────────────────────
    ops += [
        "q",
        "0.15 0.35 0.60 rg",
        "40 40 515 17 re f",
        "Q",
    ]

    # ── Línea separadora horizontal ─────────────────────────────
    def hline(y):
        ops.extend(["q", "0.6 w", "0.7 0.7 0.7 RG",
                    f"90 {y} m 505 {y} l S", "Q"])

    # ── Texto con posición ABSOLUTA usando operador Tm ──────────
    # Tm: 1 0 0 1 x y Tm  →  posición absoluta (x, y) en la página
    def put(text, x, y, size):
        ops.extend([
            "BT",
            f"/F1 {size} Tf",
            f"1 0 0 1 {x:.1f} {y:.1f} Tm",
            f"({_escape(text)}) Tj",
            "ET",
        ])

    def center(text, y, size, factor=0.52):
        put(text, _cx(text, size, factor=factor), y, size)

    def center_bold(text, y, size, factor=0.60):
        """Centra texto usando factor de ancho bold (Helvetica-Bold)."""
        ops.extend([
            "BT",
            f"/F2 {size} Tf",
            f"1 0 0 1 {_cx(text, size, factor=factor):.1f} {y:.1f} Tm",
            f"({_escape(text)}) Tj",
            "ET",
        ])

    # ── Contenido del certificado ───────────────────────────────

    # Encabezado institución
    center("EduCampus Online Academy", 790, 11)

    # Título principal
    center_bold("CERTIFICADO DE FINALIZACION", 720, 26)
    hline(710)

    # Subtítulo
    center("Se otorga el presente certificado a:", 670, 13)

    # Nombre del estudiante (grande y destacado)
    center_bold(student_name.upper(), 615, 34, factor=0.62)
    hline(600)

    # Texto curso
    center("Por haber completado satisfactoriamente el curso:", 555, 13)

    # Nombre del curso
    center_bold(f'"{course_name}"', 505, 22, factor=0.58)
    hline(488)

    # Estado y progreso
    center("Estado: APROBADO   |   Progreso: 100% Completado", 450, 13)

    # Fecha
    center(f"Fecha de emision: {date_str}", 415, 12)

    # ── Línea de firma ──────────────────────────────────────────
    ops += [
        "q", "0.8 w", "0.3 0.3 0.3 RG",
        "190 200 215 0 re S",
        "Q",
    ]
    center("Director Academico", 185, 12)
    center("EduCampus Online Academy", 168, 11)

    # ── Sello decorativo (círculo) ──────────────────────────────
    # Dibujado como cuadrado redondeado simulado con 4 arcos (bezier curves)
    cx, cy, r = 297, 265, 38
    k = r * 0.552          # factor de control bezier para círculo
    ops += [
        "q",
        "0.15 0.35 0.60 RG",
        "1.2 w",
        f"{cx} {cy + r} m",
        f"{cx + k:.1f} {cy + r:.1f} {cx + r:.1f} {cy + k:.1f} {cx + r:.1f} {cy:.1f} c",
        f"{cx + r:.1f} {cy - k:.1f} {cx + k:.1f} {cy - r:.1f} {cx} {cy - r:.1f} c",
        f"{cx - k:.1f} {cy - r:.1f} {cx - r:.1f} {cy - k:.1f} {cx - r:.1f} {cy} c",
        f"{cx - r:.1f} {cy + k:.1f} {cx - k:.1f} {cy + r:.1f} {cx} {cy + r:.1f} c",
        "S",
        "Q",
    ]
    center("SELLO", 258, 9)
    center("OFICIAL", 248, 9)

    # ── Ensamblado del PDF en bytes ─────────────────────────────
    stream = "\n".join(ops).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        (
            b"3 0 obj << /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 595 842] "
            b"/Resources << /Font << "
            b"/F1 4 0 R "
            b"/F2 5 0 R "
            b">> >> /Contents 6 0 R >> endobj\n"
        ),
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj\n",
        (
            f"6 0 obj << /Length {len(stream)} >> stream\n".encode("latin-1")
            + stream
            + b"\nendstream endobj\n"
        ),
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_offset = len(pdf)
    n = len(objects) + 1
    pdf.extend(f"xref\n0 {n}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
    pdf.extend((
        f"trailer << /Size {n} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode("latin-1"))

    file_path.write_bytes(bytes(pdf))
    return str(file_path)
