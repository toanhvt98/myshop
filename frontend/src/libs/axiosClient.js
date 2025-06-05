import axios from "axios";
import { CONFIG } from "@/global-config";

const axiosInstance = axios.create({
  baseURL: CONFIG.serverApiUrl,

  withCredentials: true,
});

axiosInstance.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === "development") console.log(response);
    return response;
  },
  (error) => Promise.reject(error),
);

export { axiosInstance as axiosClient };
