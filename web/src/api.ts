import axios from 'axios';

const base =
  window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;

export default axios.create({ baseURL: base });