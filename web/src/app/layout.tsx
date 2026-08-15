import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qiskit Intuition — Interactive Quantum Laboratory Notebook",
  description:
    "Explore quantum mechanics through interactive 3D Bloch spheres, dynamic circuit composition, wavefunction analysis, and Socratic AI guidance — styled as a physicist's notebook.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-paper text-ink antialiased">
        {children}
      </body>
    </html>
  );
}
