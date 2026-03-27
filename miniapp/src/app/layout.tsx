import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TruEst Digital — WhatsApp-боты и автоматизация для бизнеса",
  description: "Автоматизируем малый бизнес Казахстана: WhatsApp-боты для записи, каталоги, бронирование, ERP-системы. 10+ продуктов, 8 ниш, 10 городов.",
  keywords: "WhatsApp бот, автоматизация бизнеса, Казахстан, запись онлайн, CRM, ERP",
  openGraph: {
    title: "TruEst Digital — WhatsApp-боты для бизнеса КЗ",
    description: "Автоматизируем малый бизнес: боты, ERP, сайты под ключ",
    type: "website",
    locale: "ru_KZ",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
