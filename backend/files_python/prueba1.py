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
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf_stream = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        total_pages = len(pdf_reader.pages)
        lista_dataframes = []
        for i in range(len(area_tabla)):
            try:
                # Convertir a cadena antes de pasar a read_pdf
                area_tabla_str = [str(coord) for coord in area_tabla[i]]
                dfs = read_pdf(pdf_stream, area=area_tabla_str, stream=True, output_format="dataframe", pages='all')[0]
                prim_fila = dfs.columns.tolist()
                dfs.loc[-1] = prim_fila
                dfs.index = dfs.index + 1
                dfs = dfs.sort_index()
                lista_dataframes.append(dfs)
            except Exception as e:
                return {"status": "error", "message": f"Error al extraer tabla: {str(e)}"}
        dfs_con = pd.concat(lista_dataframes, ignore_index=True)
        names_col = [f"columna {i}" for i in range(dfs_con.shape[1])]
        dfs_con.columns = names_col
        num_filas_buenas = dfs_con.iloc[:, 0].notnull().sum()
        dfs_con["grupo"] = dfs_con.index // (dfs_con.shape[0] / num_filas_buenas)
        dfs_con = dfs_con.fillna(" ")
        dfs_con = dfs_con.groupby("grupo").agg(" ".join).reset_index(drop=True)
        lista_de_columnas = []
        nombres_columnas = []
        num_col_tabla = len(names_col)
        for fijo in area_cabecera:
            try:
                # Convertir a cadena antes de pasar a read_pdf
                fijo_str = [str(coord) for coord in fijo]
                df = read_pdf(pdf_stream, area=fijo_str, stream=True, output_format="dataframe", pages='all')
                if df:
                    df = pd.DataFrame(df[0])
                    columnas = df.columns.tolist()
                else:
                    columnas = [""]
                lista_de_columnas.append(columnas)
                nombres_columnas.append(f"Columna {num_col_tabla}")
                num_col_tabla += 1
            except Exception as e:
                return {"status": "error", "message": f"Error al extraer cabecera: {str(e)}"}
        df_extra = pd.DataFrame(lista_de_columnas).T
        n = dfs_con.shape[0]
        df_repetido = pd.DataFrame(np.repeat(df_extra.values, n, axis=0), columns=nombres_columnas)
        df_concatenado = pd.concat([dfs_con, df_repetido], axis=1)
        df_concatenado.fillna("", inplace=True)
        json_response = {
            "status": "success",
            "message": "Datos extraidos correctamente",
            "total_pages": total_pages,
            "resultado": df_concatenado.to_dict(orient="records")
        }
        return json_response
    except Exception as e:
        return {"status": "error", "message": f"Error general: {str(e)}"}

if __name__ == "__main__":
    input_data = sys.stdin.read()
    try:
        data = json.loads(input_data)
        base64_pdf = data['base64']
        area_tabla = data['area_tabla']
        area_cabecera = data['area_CABECERA']
        if base64_pdf and area_tabla and area_cabecera:
            resultado_json = extraer_datos_pdf(base64_pdf, area_tabla, area_cabecera)
            try:
                print(json.dumps(resultado_json, ensure_ascii=False, indent=4))
            except Exception as e:
                print(json.dumps({"error": f"Error al serializar JSON: {str(e)}"}), file=sys.stderr)
                sys.exit(1)
        else:
            print(json.dumps({"error": "Faltan parámetros en la solicitud."}))
    except Exception as e:
        print(json.dumps({"error": f"Error al procesar los datos de entrada: {str(e)}"}), file=sys.stderr)
        sys.exit(1)