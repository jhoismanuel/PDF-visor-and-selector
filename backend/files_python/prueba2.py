import base64
import pandas as pd
import numpy as np
import json
import PyPDF2
import io
from tabula import read_pdf
import sys
import os

os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["JAVA_TOOL_OPTIONS"] = "-Dorg.apache.commons.logging.Log=org.apache.commons.logging.impl.NoOpLog"

def extraer_datos_pdf(base64_pdf, area_tabla, area_cabecera):
    """
    Extrae datos de un PDF en base64 en base a coordenadas dadas y los devuelve en formato JSON.

    Args:
        base64_pdf (str): PDF codificado en base64.
        area_tabla (list): Coordenadas de la tabla principal [y1, x1, y2, x2].
        area_cabecera (list): Lista de coordenadas de la cabecera.

    Returns:
        dict: Respuesta en formato JSON con los datos extraídos o mensaje de error.
    """
    try:
        # Decodificar Base64 a binario
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf_stream = io.BytesIO(pdf_bytes)

        # Obtener número total de páginas del PDF
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        total_pages = len(pdf_reader.pages)
        # print(type(total_pages))
        # Extraer la tabla principal usando las coordenadas de 'area_tabla'
        # print(len(area_tabla))
        lista_dataframes=[]
        for i in range(0,len(area_tabla)):
            dfs = read_pdf(pdf_stream, area=area_tabla[i], stream=True, output_format="dataframe", pages=i)[0]
            #sacar el encabezado y volverlo una fila
            prim_fila=dfs.columns.tolist()
            dfs.loc[-1]=prim_fila
            dfs.index=dfs.index+1
            dfs=dfs.sort_index()
            lista_dataframes.append(dfs)
            

        dfs_con=pd.concat(lista_dataframes, ignore_index=True)
        
        # print(dfs_con)

        ########################################
        # sacar el encabezado y volverlo una fila
        # prim_fila=dfs_con.columns.tolist()
        # # print(prim_fila)
        # dfs_con.loc[-1]=prim_fila
        # dfs_con.index=dfs_con.index+1
        # dfs_con=dfs_con.sort_index()
        # print(dfs_con)
        
        
        
        names_col=[]
        for i in range (0,dfs_con.shape[1]):
            name_col = f"columna {i}"  # Concatenar la cadena y el número
            names_col.append(name_col)

        print(names_col)
        print(dfs_con.shape)

        dfs_con.columns=names_col
        
        ########################################
        
        ########################################
        # #corregir datos que se dividen en mas de 2 filas IMPORTANT PROCESS
        num_filas_buenas=dfs_con.iloc[:,0].notnull().sum()
        
        dfs_con["grupo"]=dfs_con.index//(dfs_con.shape[0]/num_filas_buenas)
        # print(dfs_con["grupo"])
        # print(dfs_con)

        dfs_con=dfs_con.fillna(" ") #Para reemplazar los espacios NaN con " "

        dfs_con=dfs_con.groupby("grupo").agg(" ".join).reset_index(drop=True)
        # print(dfs_con)


        ########################################
        # Lista para almacenar datos de las coordenadas de la cabecera
        lista_de_columnas = []
        nombres_columnas = []
        num_col_tabla=len(names_col)
        for fijo in area_cabecera:
            df = read_pdf(pdf_stream, area=fijo, stream=True, output_format="dataframe", pages="all")
            if df:
                df = pd.DataFrame(df[0])
                columnas = df.columns.tolist()
            else:
                columnas = [""]

            lista_de_columnas.append(columnas)
            nombres_columnas.append(f"Columna {num_col_tabla}")
            num_col_tabla=num_col_tabla+1

        # Convertir a DataFrame y repetir para igualar las filas de `dfs_con`
        df_extra = pd.DataFrame(lista_de_columnas).T  # Transponer para correcta alineación
        n=dfs_con.shape[0] #numero de filas items para multiplicar los valores fijos
        df_repetido = pd.DataFrame(np.repeat(df_extra.values, n, axis=0), columns=nombres_columnas)
        # print(df_repetido)
        # Concatenar con la tabla principal
        df_concatenado = pd.concat([dfs_con, df_repetido], axis=1)
        df_concatenado.fillna("", inplace=True)  # Reemplazar NaN por cadenas vacías

        # Convertir DataFrame a JSON
        json_response = {
            "status": "success",
            "message": "Datos extraidos correctamente",
            "total_pages": total_pages,
            "resultado": df_concatenado.to_dict(orient="records")
        }

        return json_response
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# INICIALIZA LA FUNCION "PROCESAR_FACTURA" PARA SU USO
# if __name__ == "__main__":
#     # Leer el JSON desde stdin
#     input_data = sys.stdin.read()

#     try:
#         # Parsear el JSON recibido
#         data = json.loads(input_data)

#         # Extraer base64, area_tabla y area_CABECERA del JSON
#         base64_pdf = data['base64']
#         area_tabla = data['area_tabla']
#         area_cabecera = data['area_CABECERA']

#         # Verificar que se hayan recibido todos los parámetros
#         if base64_pdf and area_tabla and area_cabecera:
# Procesar los datos


# INICIALIZA LA FUNCION "PROCESAR_FACTURA" PARA SU USO
if __name__ == "__main__":
    # Leer el JSON desde stdin
    input_data = sys.stdin.read()

    try:
        # Parsear el JSON recibido
        data = json.loads(input_data)

        # Extraer base64, area_tabla y area_CABECERA del JSON
        base64_pdf = data['base64']
        area_tabla = data['area_tabla']
        area_cabecera = data['area_CABECERA']

        # Verificar que se hayan recibido todos los parámetros
        if base64_pdf and area_tabla and area_cabecera:
# Procesar los datos

# area_tabla=[168.80, 21.16, 478.83, 477.60]
            # area_tabla=[212.28,27.99, 594.02,591.80 ]

# area_cabecera=[
#                 [35.61, 487.40, 50.27, 551.28],
#                 [104.73, 454.94, 116.25, 501.02],
#                 [104.73, 516.51, 117.29, 582.49],
#                 [129.86, 74.78, 148.71, 153.32],
#                 [146.62, 77.71, 158.14, 122.74],
#                 [162.33, 71.63, 179.08, 246.53],
#                 [134.05, 380.58, 148.71, 417.23],
#                 [146.62, 373.04, 158.14, 567.83],
#                 [156.04, 377.44, 170.71, 442.37],
#                 [167.56, 375.34, 180.13, 419.33],
#                 [178.87, 371.99, 193.54, 404.46],
#                 [192.70, 369.90, 204.22, 413.88]
#             ]


            resultado_json = extraer_datos_pdf(base64_pdf, area_tabla, area_cabecera)
# print(json.dumps(resultado_json))  # Salida en formato JSON
            print(json.dumps(resultado_json, ensure_ascii=False, indent=4))  # Salida en formato JSON

        else:
            print(json.dumps({"error": "Faltan parámetros en la solicitud."}))

    except Exception as e:
        print(json.dumps({"error": f"Error al procesar los datos: {str(e)}"}))
