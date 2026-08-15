import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qiskit Intuition | Interactive Physics Quantum Laboratory",
  description:
    "Explore quantum mechanics through real-time 3D Bloch Spheres, dynamic circuit composer wires, wavefunction oscilloscopes, and Socratic AI coaching.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased selection:bg-quantum-cyan/30 selection:text-quantum-cyan">
        {children}
      </body>
    </html>
  );
}
