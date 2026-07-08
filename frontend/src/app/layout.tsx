import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Chronos Stadium AI — Generative Future Engine for Mega Events",
  description:
    "Chronos Stadium AI continuously generates hundreds of possible operational futures from live stadium data, ranks them by risk, and recommends the best decisions before problems occur.",
  keywords: ["stadium operations", "AI simulation", "crowd management", "event safety", "future engine"],
  authors: [{ name: "Chronos Stadium AI" }],
  openGraph: {
    title: "Chronos Stadium AI",
    description: "The world's first Generative Future Engine for Mega Events.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-full flex flex-col antialiased`}
      >
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          {children}
          <Toaster theme="system" position="bottom-right" />
        </ThemeProvider>
      </body>
    </html>
  );
}
