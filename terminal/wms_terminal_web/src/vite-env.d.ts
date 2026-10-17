/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_STORE_API_BASE_URL?: string;
  readonly VITE_WMS_API_BASE_URL?: string;
  readonly REACT_APP_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
