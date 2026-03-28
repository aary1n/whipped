import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "./nav";
import { VerdictProvider } from "./lib/verdict-context";

export const metadata: Metadata = {
  title: "Whipped | Used Car Pricing Intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-teal-900 selection:text-teal-100">
        <VerdictProvider>
          <Nav />
          <main>{children}</main>
        </VerdictProvider>
      </body>
    </html>
  );
}
