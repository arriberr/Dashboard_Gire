import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
import openpyxl 
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"

# Autenticación básica
st.title("Dashboard GIRE")

password = st.text_input("Contraseña", type="password")

if password != "Gire2025":
    st.warning("Contraseña incorrecta")
    st.stop()


)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-positive {
        color: #10b981;
        font-weight: bold;
    }
    .kpi-negative {
        color: #ef4444;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
</style>
""", unsafe_allow_html=True)

def create_sample_data():
    """Crear datos de ejemplo para demostración"""
    np.random.seed(42)
    
    # Definir parámetros
    meses_2024 = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
    meses_2025 = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06']
    operaciones = ['Cobranzas', 'Pagos', 'Otros']
    canales = ['Digital', 'Físico', 'Phigital']
    tipos = ['Real', 'Presupuesto']
    
    data = []
    
    # Generar datos para 2024 (solo Real)
    for mes in meses_2024:
        for operacion in operaciones:
            for canal in canales:
                base_trx = np.random.randint(800, 1500) if operacion == 'Cobranzas' else np.random.randint(200, 600)
                base_ingresos = base_trx * np.random.uniform(60, 120)
                base_recaudacion = base_ingresos * np.random.uniform(0.85, 0.98)
                
                data.append({
                    'AñoMes': mes,
                    'Tipo_Operacion': operacion,
                    'Tipo_Canal': canal,
                    'Trx': base_trx,
                    'Ingresos': int(base_ingresos),
                    'Recaudacion': int(base_recaudacion),
                    'Tipo': 'Real'
                })
    
    # Generar datos para 2025 (Real y Presupuesto)
    for mes in meses_2025:
        for operacion in operaciones:
            for canal in canales:
                for tipo in tipos:
                    base_trx = np.random.randint(900, 1600) if operacion == 'Cobranzas' else np.random.randint(250, 650)
                    base_ingresos = base_trx * np.random.uniform(65, 125)
                    base_recaudacion = base_ingresos * np.random.uniform(0.88, 0.98)
                    
                    # Ajustar para presupuesto (más conservador)
                    if tipo == 'Presupuesto':
                        base_trx = int(base_trx * 0.95)
                        base_ingresos = int(base_ingresos * 0.93)
                        base_recaudacion = int(base_recaudacion * 0.94)
                    
                    data.append({
                        'AñoMes': mes,
                        'Tipo_Operacion': operacion,
                        'Tipo_Canal': canal,
                        'Trx': base_trx,
                        'Ingresos': int(base_ingresos),
                        'Recaudacion': int(base_recaudacion),
                        'Tipo': tipo
                    })
    
    return pd.DataFrame(data)

def load_data():
    """Cargar datos desde archivo o usar datos de ejemplo"""
    if 'df' not in st.session_state:
        st.session_state.df = create_sample_data()
    return st.session_state.df

def calculate_metrics(df_filtered):
    """Calcular métricas principales"""
    # Separar datos por año y tipo
    real_2025 = df_filtered[(df_filtered['AñoMes'].str.startswith('2025')) & (df_filtered['Tipo'] == 'Real')]
    presupuesto_2025 = df_filtered[(df_filtered['AñoMes'].str.startswith('2025')) & (df_filtered['Tipo'] == 'Presupuesto')]
    real_2024 = df_filtered[(df_filtered['AñoMes'].str.startswith('2024')) & (df_filtered['Tipo'] == 'Real')]
    
    # Calcular totales
    metrics = {}
    
    # Totales 2025 Real
    metrics['real_2025'] = {
        'trx': real_2025['Trx'].sum(),
        'ingresos': real_2025['Ingresos'].sum(),
        'recaudacion': real_2025['Recaudacion'].sum()
    }
    
    # Totales 2025 Presupuesto
    metrics['presupuesto_2025'] = {
        'trx': presupuesto_2025['Trx'].sum(),
        'ingresos': presupuesto_2025['Ingresos'].sum(),
        'recaudacion': presupuesto_2025['Recaudacion'].sum()
    }
    
    # Totales 2024 Real
    metrics['real_2024'] = {
        'trx': real_2024['Trx'].sum(),
        'ingresos': real_2024['Ingresos'].sum(),
        'recaudacion': real_2024['Recaudacion'].sum()
    }
    
    # Calcular variaciones
    metrics['var_presupuesto'] = {}
    metrics['var_año_anterior'] = {}
    
    for key in ['trx', 'ingresos', 'recaudacion']:
        # Variación vs Presupuesto
        if metrics['presupuesto_2025'][key] > 0:
            metrics['var_presupuesto'][key] = ((metrics['real_2025'][key] - metrics['presupuesto_2025'][key]) / metrics['presupuesto_2025'][key]) * 100
        else:
            metrics['var_presupuesto'][key] = 0
            
        # Variación vs Año Anterior
        if metrics['real_2024'][key] > 0:
            metrics['var_año_anterior'][key] = ((metrics['real_2025'][key] - metrics['real_2024'][key]) / metrics['real_2024'][key]) * 100
        else:
            metrics['var_año_anterior'][key] = 0
    
    # Precio promedio por transacción
    metrics['precio_prom_2025'] = metrics['real_2025']['ingresos'] / metrics['real_2025']['trx'] if metrics['real_2025']['trx'] > 0 else 0
    metrics['precio_prom_2024'] = metrics['real_2024']['ingresos'] / metrics['real_2024']['trx'] if metrics['real_2024']['trx'] > 0 else 0
    
    return metrics

def format_number(num):
    """Formatear números"""
    return f"{num:,.0f}".replace(',', '.')

def format_currency(num):
    """Formatear moneda"""
    return f"${num:,.0f}".replace(',', '.')

def format_percentage(num):
    """Formatear porcentaje"""
    return f"{num:.1f}%"

def create_monthly_comparison_chart(df_filtered):
    """Crear gráfico de comparación mensual"""
    # Agrupar datos por mes y tipo
    monthly_data = df_filtered.groupby(['AñoMes', 'Tipo']).agg({
        'Trx': 'sum',
        'Ingresos': 'sum',
        'Recaudacion': 'sum'
    }).reset_index()
    
    # Crear gráfico con subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Transacciones', 'Ingresos', 'Recaudación', 'Comparación YoY'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gráfico de Transacciones
    real_data = monthly_data[monthly_data['Tipo'] == 'Real']
    presup_data = monthly_data[monthly_data['Tipo'] == 'Presupuesto']
    
    fig.add_trace(
        go.Bar(x=real_data['AñoMes'], y=real_data['Trx'], name='Real - Trx', marker_color='#3b82f6'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=presup_data['AñoMes'], y=presup_data['Trx'], name='Presupuesto - Trx', marker_color='#10b981'),
        row=1, col=1
    )
    
    # Gráfico de Ingresos
    fig.add_trace(
        go.Scatter(x=real_data['AñoMes'], y=real_data['Ingresos'], mode='lines+markers', name='Real - Ingresos', line=dict(color='#ef4444', width=3)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=presup_data['AñoMes'], y=presup_data['Ingresos'], mode='lines+markers', name='Presupuesto - Ingresos', line=dict(color='#f59e0b', width=3)),
        row=1, col=2
    )
    
    # Gráfico de Recaudación
    fig.add_trace(
        go.Bar(x=real_data['AñoMes'], y=real_data['Recaudacion'], name='Real - Recaudación', marker_color='#8b5cf6'),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=presup_data['AñoMes'], y=presup_data['Recaudacion'], name='Presupuesto - Recaudación', marker_color='#06b6d4'),
        row=2, col=1
    )
    
    # Comparación año contra año (solo 2025 vs 2024)
    real_2025 = real_data[real_data['AñoMes'].str.startswith('2025')]
    real_2024 = df_filtered[(df_filtered['AñoMes'].str.startswith('2024')) & (df_filtered['Tipo'] == 'Real')].groupby('AñoMes').agg({'Ingresos': 'sum'}).reset_index()
    
    fig.add_trace(
        go.Scatter(x=real_2025['AñoMes'], y=real_2025['Ingresos'], mode='lines+markers', name='2025', line=dict(color='#dc2626', width=4)),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="Análisis Comparativo Financiero")
    return fig

def create_distribution_chart(df_filtered):
    """Crear gráfico de distribución por canal"""
    # Datos para 2025 Real
    canal_data = df_filtered[(df_filtered['AñoMes'].str.startswith('2025')) & (df_filtered['Tipo'] == 'Real')]
    canal_summary = canal_data.groupby('Tipo_Canal').agg({
        'Trx': 'sum',
        'Ingresos': 'sum'
    }).reset_index()
    
    fig = px.pie(canal_summary, values='Trx', names='Tipo_Canal', 
                 title='Distribución de Transacciones por Canal (2025)',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    return fig

def main():
    # Título principal
    st.markdown('<h1 class="main-header">💰 Dashboard Financiero Interactivo</h1>', unsafe_allow_html=True)
    
    # Sidebar para filtros
    st.sidebar.header("🎛️ Filtros")
    
    # Cargar datos
    df = load_data()
    
    # Opción para cargar archivo
    uploaded_file = st.sidebar.file_uploader("📁 Cargar archivo Excel", type=['xlsx', 'xls'])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.session_state.df = df
            st.sidebar.success("¡Archivo cargado exitosamente!")
        except Exception as e:
            st.sidebar.error(f"Error al cargar archivo: {e}")
    
    # Mostrar información del dataset
    st.sidebar.info(f"📊 Total de registros: {len(df)}")
    
    # Filtros
    operaciones = ['Todos'] + list(df['Tipo_Operacion'].unique())
    canales = ['Todos'] + list(df['Tipo_Canal'].unique())
    meses = ['Todos'] + sorted(list(df['AñoMes'].str[-2:].unique()))
    
    selected_operacion = st.sidebar.selectbox("🏪 Tipo de Operación", operaciones)
    selected_canal = st.sidebar.selectbox("📱 Canal", canales)
    selected_mes = st.sidebar.selectbox("📅 Mes", meses)
    
    # Aplicar filtros
    df_filtered = df.copy()
    if selected_operacion != 'Todos':
        df_filtered = df_filtered[df_filtered['Tipo_Operacion'] == selected_operacion]
    if selected_canal != 'Todos':
        df_filtered = df_filtered[df_filtered['Tipo_Canal'] == selected_canal]
    if selected_mes != 'Todos':
        df_filtered = df_filtered[df_filtered['AñoMes'].str.endswith(selected_mes)]
    
    # Calcular métricas
    metrics = calculate_metrics(df_filtered)
    
    # KPIs principales
    st.subheader("📈 Indicadores Clave de Desempeño")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💳 Transacciones 2025",
            value=format_number(metrics['real_2025']['trx']),
            delta=f"{format_percentage(metrics['var_presupuesto']['trx'])} vs Presup."
        )
    
    with col2:
        st.metric(
            label="💰 Ingresos 2025",
            value=format_currency(metrics['real_2025']['ingresos']),
            delta=f"{format_percentage(metrics['var_presupuesto']['ingresos'])} vs Presup."
        )
    
    with col3:
        st.metric(
            label="🏦 Recaudación 2025",
            value=format_currency(metrics['real_2025']['recaudacion']),
            delta=f"{format_percentage(metrics['var_año_anterior']['recaudacion'])} vs 2024"
        )
    
    with col4:
        precio_diff = metrics['precio_prom_2025'] - metrics['precio_prom_2024']
        st.metric(
            label="💵 Precio Promedio",
            value=format_currency(metrics['precio_prom_2025']),
            delta=f"{format_currency(precio_diff)} vs 2024"
        )
    
    # Gráficos principales
    st.subheader("📊 Análisis Visual")
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencias", "🥧 Distribución", "📋 Tabla Resumen", "🚨 Alertas"])
    
    with tab1:
        fig_monthly = create_monthly_comparison_chart(df_filtered)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig_dist = create_distribution_chart(df_filtered)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Gráfico de evolución por operación
            op_data = df_filtered[(df_filtered['AñoMes'].str.startswith('2025')) & (df_filtered['Tipo'] == 'Real')]
            op_summary = op_data.groupby('Tipo_Operacion')['Ingresos'].sum().reset_index()
            fig_op = px.bar(op_summary, x='Tipo_Operacion', y='Ingresos',
                           title='Ingresos por Tipo de Operación (2025)',
                           color='Ingresos', color_continuous_scale='viridis')
            st.plotly_chart(fig_op, use_container_width=True)
    
    with tab3:
        st.subheader("📋 Resumen Comparativo")
        
        # Crear tabla resumen
        summary_data = {
            'Métrica': ['Transacciones', 'Ingresos', 'Recaudación', 'Precio Promedio'],
            'Real 2025': [
                format_number(metrics['real_2025']['trx']),
                format_currency(metrics['real_2025']['ingresos']),
                format_currency(metrics['real_2025']['recaudacion']),
                format_currency(metrics['precio_prom_2025'])
            ],
            'Presupuesto 2025': [
                format_number(metrics['presupuesto_2025']['trx']),
                format_currency(metrics['presupuesto_2025']['ingresos']),
                format_currency(metrics['presupuesto_2025']['recaudacion']),
                '-'
            ],
            'Real 2024': [
                format_number(metrics['real_2024']['trx']),
                format_currency(metrics['real_2024']['ingresos']),
                format_currency(metrics['real_2024']['recaudacion']),
                format_currency(metrics['precio_prom_2024'])
            ],
            'Var. vs Presup.': [
                format_percentage(metrics['var_presupuesto']['trx']),
                format_percentage(metrics['var_presupuesto']['ingresos']),
                format_percentage(metrics['var_presupuesto']['recaudacion']),
                '-'
            ],
            'Var. vs 2024': [
                format_percentage(metrics['var_año_anterior']['trx']),
                format_percentage(metrics['var_año_anterior']['ingresos']),
                format_percentage(metrics['var_año_anterior']['recaudacion']),
                format_currency(precio_diff)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    with tab4:
        st.subheader("🚨 Alertas e Insights")
        
        # Generar alertas basadas en las métricas
        alertas = []
        
        if metrics['var_presupuesto']['ingresos'] < -5:
            alertas.append({
                'tipo': 'error',
                'mensaje': f"⚠️ ALERTA: Los ingresos están {format_percentage(abs(metrics['var_presupuesto']['ingresos']))} por debajo del presupuesto"
            })
        elif metrics['var_presupuesto']['ingresos'] > 5:
            alertas.append({
                'tipo': 'success',
                'mensaje': f"✅ EXCELENTE: Los ingresos superan el presupuesto en {format_percentage(metrics['var_presupuesto']['ingresos'])}"
            })
        
        if metrics['var_año_anterior']['trx'] > 10:
            alertas.append({
                'tipo': 'info',
                'mensaje': f"📈 CRECIMIENTO: Las transacciones crecieron {format_percentage(metrics['var_año_anterior']['trx'])} vs 2024"
            })
        
        if precio_diff > 0:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f"💰 El precio promedio aumentó {format_currency(precio_diff)} respecto a 2024"
            })
        
        # Mostrar alertas
        if alertas:
            for alerta in alertas:
                if alerta['tipo'] == 'error':
                    st.error(alerta['mensaje'])
                elif alerta['tipo'] == 'success':
                    st.success(alerta['mensaje'])
                elif alerta['tipo'] == 'info':
                    st.info(alerta['mensaje'])
                elif alerta['tipo'] == 'warning':
                    st.warning(alerta['mensaje'])
        else:
            st.info("📊 No hay alertas críticas en este momento")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 Dashboard Transacciones Interactivo | Desarrollado con Streamlit y Python</p>
        <p>📁 Carga tu archivo Excel con las columnas: AñoMes, Tipo_Operacion, Tipo_Canal, Trx, Ingresos, Recaudacion, Tipo</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()