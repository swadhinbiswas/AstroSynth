import type { Metadata } from "next";
import "./globals.css";
import { Navbar, Footer } from "@/components/Navbar";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "AstroSynth — AI Exoplanet Discovery Platform",
  description: "Classify Kepler, K2 and TESS observations with explainable AI. NASA Space Apps Challenge 2025.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#030014] text-white antialiased">
        <Providers>
          <Navbar />
          <main className="mx-auto max-w-7xl px-6">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
