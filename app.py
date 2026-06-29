"""
ASECRA — Centro de Acopio
App de gestión de envíos y voluntarios (Streamlit).
"""
import sqlite3
import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "asecra.db"

ESTADOS = ["Pendiente", "En preparación", "Listo para enviar", "Enviado", "Entregado"]
TIPOS = ["—", "Ropa", "Víveres", "Medicinas", "Agua", "Insumos médicos", "Aseo personal", "Varios"]
CATEGORIAS = [
    "Hospital", "Ambulatorio / Salud", "Institución / Salud", "Ancianato", "Religioso / Ancianato",
    "Parroquia", "Colegio", "Fundación", "Damnificados", "Damnificados / Familias",
    "Comunidad / Damnificados", "Comunidad", "Rescatistas", "Rescatistas (animales)", "Cruz Roja",
    "Bomberos", "Protección Civil", "Servicio / Logística", "Persona / Contacto", "Hospital / Persona",
]
VOLUNTARIADO_OPC = [
    "Exalumna", "Alumna", "Voluntaria", "Voluntario", "Voluntaria USB",
    "Mamá de alumna", "Papá", "CR", "CCR", "CUMIS UCV", "Otro",
]

SEED_LUGARES = [
    ("Rescatistas Brasileros", "Rescatistas", "", "", "—"),
    ("12 familias casco histórico de La Guaira", "Damnificados / Familias", "", "12 familias", "—"),
    ("Hospital del Seguro Social", "Hospital", "", "", "—"),
    ("Cruz Roja San Bernardino", "Cruz Roja", "", "", "—"),
    ("Parroquia Artigas", "Parroquia", "", "", "—"),
    ("Playa Grande", "Comunidad / Damnificados", "", "Enviar 2 veces", "—"),
    ("Hospital Militar (Emergencia)", "Hospital", "", "Emergencia", "—"),
    ("Fundana", "Fundación", "Gabriela Pérez", "", "—"),
    ("Ancianato Caricuao", "Ancianato", "", "", "—"),
    ("Parroquia Altagracia", "Parroquia", "", "", "—"),
    ("Anciano Caricuao", "Ancianato", "", "", "—"),
    ("Colegio Francisco Pimentel", "Colegio", "", "", "—"),
    ("Prof. Física CSI", "Persona / Contacto", "", "(revisar lectura)", "—"),
    ("IVSS Av. Baralt", "Institución / Salud", "", "Canjes (revisar lectura)", "—"),
    ("Cruz Roja San Bernardino", "Cruz Roja", "", "Repetido en la lista", "—"),
    ("Hospital Militar (Emergencias)", "Hospital", "", "Emergencias", "—"),
    ("Familia damnificada La Guaira", "Damnificados", "Jennifer López", "", "—"),
    ("Hospital Vargas", "Hospital", "", "Lista larga", "—"),
    ("Elizabeth Totu", "Persona / Contacto", "Elizabeth Totu", "", "Ropa"),
    ("Hospital Pérez Carreño", "Hospital", "Yulimar Pérez", "Piso 6 — cirugía", "—"),
    ("Juan Pablo Sayegh (Universitario)", "Hospital / Persona", "Juan Pablo Sayegh", "Hospital Universitario", "—"),
    ("Hospital de Pariata", "Hospital", "", "", "—"),
    ("Hospital Pérez de León", "Hospital", "", "", "—"),
    ("Tu Gruero", "Servicio / Logística", "", "(revisar lectura)", "—"),
    ("María Gabriela Lovera", "Persona / Contacto", "María Gabriela Lovera", "", "—"),
    ("Ambulatorio Rafael Martínez", "Ambulatorio / Salud", "Patricia Grossman", "Medicinas (full)", "Medicinas"),
    ("Andrea Prieto", "Damnificados", "Andrea Prieto", "Ropa — damnificado", "Ropa"),
    ("Elias Elia", "Damnificados", "Elias Elia", "La Guaira, varios", "—"),
    ("Prof. Ernesto", "Persona / Contacto", "Prof. Ernesto", "Entrega directa", "Varios"),
    ("El Junquito", "Comunidad", "", "", "—"),
    ("Hospital Ortopédico Infantil", "Hospital", "", "", "—"),
    ("Fundación Beethoven", "Fundación", "", "", "—"),
    ("Rescatistas perros Chacao", "Rescatistas (animales)", "", "", "—"),
    ("Club Caraballeda", "Comunidad / Damnificados", "", "", "—"),
    ("Barrio Erazo", "Comunidad", "", "", "—"),
    ("Hermanas Pobres de Maiquetía", "Religioso / Ancianato", "", "", "—"),
    ("Hospital Universitario", "Hospital", "", "", "—"),
    ("Bomberos UCV", "Bomberos", "", "", "—"),
    ("Rescatistas Ecuador", "Rescatistas", "", "", "—"),
    ("Parroquia Santa Rosalía", "Parroquia", "", "", "—"),
    ("Protección Civil La Guaira", "Protección Civil", "", "", "—"),
]

# (nombre, celular, voluntariado) — transcrito de las hojas
SEED_VOLUNTARIOS = [
    ("Mayanta Yintino", "04143226600", "Sin clasificar"),
    ("Marisol Guevara", "04122248684", "CCR"),
    ("José Mendoza", "04141878144", "CR"),
    ("Jackie Bandres", "04149905331", "CR"),
    ("Elena Borges", "04145313631", "CR"),
    ("María Luisa Herrera", "04143268493", "CR"),
    ("Yosman Velázquez", "04141066116", "CUMIS UCV"),
    ("César El Kadi", "04242294229", "CUMIS UCV"),
    ("Mónica Piña", "04143184016", "Exalumna"),
    ("Eugenia Piña", "04143365826", "Exalumna"),
    ("Cristina Ballesteros", "04211673066", "Voluntaria USB"),
    ("Mariana Lozano", "04143113872", "CR"),
    ("Chelena Díaz", "04241956462", "CCR"),
    ("María Daniela Domínguez", "04140331144", "Exalumna"),
    ("Daniela Silva", "04122341764", "Voluntaria"),
    ("Vivianna Molino", "04143907290", "Exalumna"),
    ("Anastasia Almea", "04122847544", "Alumna"),
    ("Claudia C. Lugo", "04120356323", "Mamá de alumna"),
    ("Maia Traegnis Wetter", "04129098366", "Voluntaria"),
    ("Reece Graham", "04129098366", "Voluntario"),
    ("María Elena Sosa", "04142930015", "Exalumna"),
    ("Elisa Elia", "04241355087", "Alumna"),
    ("Paula Basmagi", "04242324411", "Voluntaria"),
    ("Sarah Soriano", "04142362564", "Sin clasificar"),
    ("Daniela Castro", "04241416051", "Exalumna"),
    ("María Isabel Aristeguieta", "04125203810", "Exalumna"),
    ("Helena Marcano", "04143000749", "Exalumna"),
    ("Corina Serrano", "04126303453", "Alumna"),
    ("Miguel Vázquez", "04143332231", "Papá ex-alumnas"),
    ("Anabella Paolini", "04143312002", "Voluntaria"),
    ("Federika Ziadie", "04125483726", "Exalumna"),
    ("Miled Ziadie", "04241918739", "Voluntaria"),
    ("Carolina Blank", "04142629392", "Voluntaria"),
    ("María Pía Meda", "04142629392", "Voluntaria"),
    ("Andrea Kohler", "04241708934", "Alumna"),
    ("Ana Isabel Santiago", "04220240244", "Alumna"),
    ("Priscilla González", "04143377401", "Alumna"),
    ("Francisco Santiago M.", "04141062866", "CCR"),
    ("Mercedes Mejía", "04122432154", "Mamá Cristo Rey"),
    ("Nelson Rector", "04123901120", "Papá Cristo Rey"),
    ("Asdrúbal Serrano", "04143095891", "Papá CR 3°-5°"),
    ("Mariana Hernández", "04126211011", "Sin clasificar"),
    ("Leandro Rossi", "04141157351", "CR"),
    ("Anadela Sanabria", "04123724101", "Exalumna"),
]


# ----------------------------- base de datos -----------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def stamp():
    return dt.datetime.now().strftime("%d/%m/%Y %H:%M")


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS lugares(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lugar TEXT, categoria TEXT, contacto TEXT, detalle TEXT,
        tipo TEXT, articulos TEXT, estado TEXT, responsable TEXT,
        actualizado TEXT)""")

    # voluntarios: migrar si viene de un esquema viejo (sin 'celular')
    cur.execute("""CREATE TABLE IF NOT EXISTS voluntarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, celular TEXT, voluntariado TEXT, registrado TEXT)""")
    cols = [r[1] for r in cur.execute("PRAGMA table_info(voluntarios)").fetchall()]
    if "celular" not in cols:
        cur.execute("DROP TABLE voluntarios")
        cur.execute("""CREATE TABLE voluntarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, celular TEXT, voluntariado TEXT, registrado TEXT)""")

    cur.execute("SELECT COUNT(*) FROM lugares")
    if cur.fetchone()[0] == 0:
        now = stamp()
        for lugar, cat, cont, det, tipo in SEED_LUGARES:
            estado = "Entregado" if lugar == "Andrea Prieto" else "Pendiente"
            cur.execute(
                "INSERT INTO lugares(lugar,categoria,contacto,detalle,tipo,articulos,estado,responsable,actualizado)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (lugar, cat, cont, det, tipo, "", estado, "—", now))

    cur.execute("SELECT COUNT(*) FROM voluntarios")
    if cur.fetchone()[0] == 0:
        now = stamp()
        for nombre, celular, vol in SEED_VOLUNTARIOS:
            cur.execute(
                "INSERT INTO voluntarios(nombre,celular,voluntariado,registrado) VALUES(?,?,?,?)",
                (nombre, celular, vol, now))

    conn.commit()
    conn.close()


def load_lugares():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM lugares ORDER BY id", conn)
    conn.close()
    return df


def load_voluntarios():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM voluntarios ORDER BY nombre", conn)
    conn.close()
    return df


def add_voluntario(nombre, celular, voluntariado):
    conn = get_conn()
    conn.execute(
        "INSERT INTO voluntarios(nombre,celular,voluntariado,registrado) VALUES(?,?,?,?)",
        (nombre, celular, voluntariado, stamp()))
    conn.commit()
    conn.close()


def delete_voluntario(vid):
    conn = get_conn()
    conn.execute("DELETE FROM voluntarios WHERE id=?", (vid,))
    conn.commit()
    conn.close()


def add_lugar(lugar, categoria, contacto, detalle):
    conn = get_conn()
    conn.execute(
        "INSERT INTO lugares(lugar,categoria,contacto,detalle,tipo,articulos,estado,responsable,actualizado)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        (lugar, categoria, contacto, detalle, "—", "", "Pendiente", "—", stamp()))
    conn.commit()
    conn.close()


def update_lugar(row):
    conn = get_conn()
    conn.execute(
        "UPDATE lugares SET lugar=?,categoria=?,contacto=?,detalle=?,tipo=?,articulos=?,estado=?,responsable=?,actualizado=? WHERE id=?",
        (row["lugar"], row["categoria"], row["contacto"], row["detalle"], row["tipo"],
         row["articulos"], row["estado"], row["responsable"], stamp(), int(row["id"])))
    conn.commit()
    conn.close()


def delete_lugar(lid):
    conn = get_conn()
    conn.execute("DELETE FROM lugares WHERE id=?", (lid,))
    conn.commit()
    conn.close()


# ----------------------------- UI -----------------------------
st.set_page_config(page_title="ASECRA · Centro de Acopio", page_icon="📦", layout="wide")
init_db()

st.markdown("""
<style>
  .block-container{padding-top:1.4rem;max-width:1200px}
  .asecra-head{background:#1b2a33;color:#f3ead8;padding:16px 20px;border-radius:12px;
    border-left:6px solid #bb432c;margin-bottom:8px}
  .asecra-head h1{margin:0;font-size:1.7rem;letter-spacing:.04em}
  .asecra-head p{margin:4px 0 0;color:#d8c3a0;font-size:.85rem}
  div[data-testid="stMetricValue"]{font-size:1.6rem}
  .vcard{background:#fff;border:1px solid #d8c3a0;border-left:5px solid #bb432c;
    border-radius:10px;padding:11px 14px;margin-bottom:10px}
  .vcard .nm{font-weight:700;font-size:1.02rem;color:#1b2a33}
  .vcard .ph{font-family:monospace;font-size:.95rem;color:#1b2a33;margin-top:2px}
  .vcard .bg{display:inline-block;background:#ece0c9;color:#5e4d33;font-size:.7rem;
    font-weight:600;padding:2px 9px;border-radius:20px;margin-top:6px}
</style>
<div class="asecra-head">
  <h1>📦 ASECRA — Centro de Acopio</h1>
  <p>Gestión de envíos y voluntarios · La Guaira &nbsp;|&nbsp; Ref: 0414-2216670 (Ale)</p>
</div>
""", unsafe_allow_html=True)

vol_df = load_voluntarios()
resp_opciones = ["—"] + vol_df["nombre"].dropna().tolist() if not vol_df.empty else ["—"]

tab_lugares, tab_vol, tab_resumen = st.tabs(
    ["📍 Lugares para enviar", "🙋 Voluntarios", "📊 Resumen"])

# ===================== LUGARES =====================
with tab_lugares:
    lug = load_lugares()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total lugares", len(lug))
    c2.metric("Pendientes", int((lug["estado"] == "Pendiente").sum()))
    c3.metric("Enviados", int((lug["estado"] == "Enviado").sum()))
    c4.metric("Entregados", int((lug["estado"] == "Entregado").sum()))

    f1, f2 = st.columns([2, 3])
    filtro_estado = f1.selectbox("Filtrar por estado", ["Todos"] + ESTADOS)
    busqueda = f2.text_input("Buscar (lugar, contacto, categoría o artículo)", "")

    vista = lug.copy()
    if filtro_estado != "Todos":
        vista = vista[vista["estado"] == filtro_estado]
    if busqueda.strip():
        q = busqueda.strip().lower()
        mask = vista[["lugar", "contacto", "categoria", "articulos", "detalle"]] \
            .fillna("").astype(str).apply(lambda r: q in " ".join(r).lower(), axis=1)
        vista = vista[mask]

    st.caption("Edita en la tabla y pulsa **Guardar cambios**. Asigna un **responsable** a cada envío "
               "para que dos personas no tomen la misma tarea.")
    edit = st.data_editor(
        vista, key="editor_lugares", use_container_width=True, hide_index=True, num_rows="fixed",
        column_order=["lugar", "categoria", "contacto", "detalle", "tipo",
                      "articulos", "estado", "responsable", "actualizado"],
        column_config={
            "id": None,
            "lugar": st.column_config.TextColumn("Lugar / Destinatario", width="medium"),
            "categoria": st.column_config.SelectboxColumn("Categoría", options=CATEGORIAS),
            "contacto": st.column_config.TextColumn("Contacto"),
            "detalle": st.column_config.TextColumn("Detalle / Notas"),
            "tipo": st.column_config.SelectboxColumn("Tipo donación", options=TIPOS),
            "articulos": st.column_config.TextColumn("Qué enviar (artículos)", width="large"),
            "estado": st.column_config.SelectboxColumn("Estado", options=ESTADOS, required=True),
            "responsable": st.column_config.SelectboxColumn("Responsable", options=resp_opciones),
            "actualizado": st.column_config.TextColumn("Últ. actualización", disabled=True),
        },
    )
    if st.button("💾 Guardar cambios", type="primary"):
        orig = lug.set_index("id")
        cambios = 0
        for _, row in edit.iterrows():
            rid = int(row["id"])
            if rid in orig.index:
                before = orig.loc[rid]
                campos = ["lugar", "categoria", "contacto", "detalle", "tipo",
                          "articulos", "estado", "responsable"]
                if any(str(before[c]) != str(row[c]) for c in campos):
                    update_lugar(row)
                    cambios += 1
        st.success(f"Guardado. {cambios} registro(s) actualizado(s).")
        st.rerun()

    st.divider()
    with st.expander("➕ Agregar un lugar nuevo"):
        with st.form("form_lugar", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            nl = cc1.text_input("Lugar / Destinatario *")
            nc = cc2.selectbox("Categoría", CATEGORIAS)
            cc3, cc4 = st.columns(2)
            ncont = cc3.text_input("Contacto / Referencia")
            ndet = cc4.text_input("Detalle / Notas")
            if st.form_submit_button("Agregar lugar", type="primary"):
                if nl.strip():
                    add_lugar(nl.strip(), nc, ncont.strip(), ndet.strip())
                    st.success(f'Agregado: "{nl.strip()}"')
                    st.rerun()
                else:
                    st.error("El nombre del lugar es obligatorio.")
    with st.expander("🗑️ Eliminar un lugar"):
        if not lug.empty:
            opt = {f'{r.id} · {r.lugar}': int(r.id) for r in lug.itertuples()}
            sel = st.selectbox("Lugar a eliminar", list(opt.keys()))
            if st.button("Eliminar lugar seleccionado"):
                delete_lugar(opt[sel]); st.warning("Lugar eliminado."); st.rerun()

    st.download_button("⤓ Descargar lista (CSV / Excel)",
        data=lug.drop(columns=["id"]).to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="asecra_lugares.csv", mime="text/csv")

# ===================== VOLUNTARIOS =====================
with tab_vol:
    st.subheader("Registrar voluntario")
    with st.form("form_vol", clear_on_submit=True):
        v1, v2, v3 = st.columns([3, 2, 2])
        vnombre = v1.text_input("Nombre *")
        vcel = v2.text_input("Celular *")
        vsel = v3.selectbox("Voluntariado", VOLUNTARIADO_OPC)
        votro = st.text_input("Si elegiste «Otro», especifica aquí", "")
        if st.form_submit_button("Registrar", type="primary"):
            vol_val = votro.strip() if vsel == "Otro" and votro.strip() else vsel
            if vnombre.strip() and vcel.strip():
                dup = vol_df[(vol_df["nombre"].str.strip().str.lower() == vnombre.strip().lower())
                             & (vol_df["celular"].str.strip() == vcel.strip())] if not vol_df.empty else pd.DataFrame()
                if not dup.empty:
                    st.warning("Ya existe un voluntario con ese nombre y celular. No se duplicó.")
                else:
                    add_voluntario(vnombre.strip(), vcel.strip(), vol_val)
                    st.success(f"¡Registrado, {vnombre.strip()}!")
                    st.rerun()
            else:
                st.error("Nombre y celular son obligatorios.")

    st.divider()
    vol_df = load_voluntarios()
    fb1, fb2 = st.columns([2, 3])
    cats_vol = ["Todos"] + sorted(vol_df["voluntariado"].dropna().unique().tolist()) if not vol_df.empty else ["Todos"]
    fvol = fb1.selectbox("Filtrar por voluntariado", cats_vol)
    bvol = fb2.text_input("Buscar voluntario (nombre o celular)", "")

    vv = vol_df.copy()
    if fvol != "Todos":
        vv = vv[vv["voluntariado"] == fvol]
    if bvol.strip():
        q = bvol.strip().lower()
        vv = vv[vv.apply(lambda r: q in f'{r["nombre"]} {r["celular"]}'.lower(), axis=1)]

    st.subheader(f"Voluntarios ({len(vv)} de {len(vol_df)})")
    if vv.empty:
        st.info("No hay voluntarios que coincidan.")
    else:
        cols = st.columns(2)
        for i, r in enumerate(vv.itertuples()):
            with cols[i % 2]:
                st.markdown(
                    f'<div class="vcard"><div class="nm">{r.nombre}</div>'
                    f'<div class="ph">{r.celular}</div>'
                    f'<span class="bg">{r.voluntariado}</span></div>',
                    unsafe_allow_html=True)

        with st.expander("🗑️ Dar de baja un voluntario"):
            optv = {f'{r.nombre} · {r.celular}': int(r.id) for r in vol_df.itertuples()}
            selv = st.selectbox("Voluntario", list(optv.keys()))
            if st.button("Dar de baja"):
                delete_voluntario(optv[selv]); st.warning("Voluntario dado de baja."); st.rerun()

    st.download_button("⤓ Descargar voluntarios (CSV / Excel)",
        data=vol_df.drop(columns=["id"]).to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="asecra_voluntarios.csv", mime="text/csv")

# ===================== RESUMEN =====================
with tab_resumen:
    lug = load_lugares()
    vol_df = load_voluntarios()
    st.subheader("Envíos por estado")
    st.bar_chart(lug["estado"].value_counts().reindex(ESTADOS, fill_value=0))
    st.subheader("Voluntarios por voluntariado")
    if vol_df.empty:
        st.info("Sin voluntarios aún.")
    else:
        st.bar_chart(vol_df["voluntariado"].value_counts())
