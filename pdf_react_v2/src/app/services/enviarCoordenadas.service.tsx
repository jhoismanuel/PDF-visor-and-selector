import axios from "axios";
import { CONFIG } from "./configuracion.service";

const url = CONFIG.url + CONFIG.versionApi;

export const postCoordenadas = async (enviarParametros:any) => {
    try {
        const response = await axios.post(`${url}/coordenadas`, JSON.stringify(enviarParametros), {
            headers: {
                // 'Authorization': 'Bearer ' + token,
                'Content-Type': 'multipart/form-data',
            },
        });
        console.log(response, 'RESPONSE UPLOAD');
        return response;
    } catch (error) {
        console.error('Error al enviar el json:', error);
        return error.response;
    }
};
