import axios from "axios";
import backurl from "./_const";
const axiosGraphInfo = axios.create({
  baseURL: backurl,
});

export default axiosGraphInfo;