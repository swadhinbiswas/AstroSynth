/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  output: "standalone",
  env: { NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1" },
};
export default config;
