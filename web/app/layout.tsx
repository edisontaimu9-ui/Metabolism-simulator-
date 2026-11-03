export const metadata = { title: "Metabolism Simulator", description: "Chakudya metabolism simulation" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><meta name="viewport" content="width=device-width, initial-scale=1" /></head>
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#f6f7f5", color: "#1d2420" }}>
        {children}
      </body>
    </html>
  );
}
