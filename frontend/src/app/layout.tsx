import "./globals.css"
import AuthProvider from "../components/AuthProvider"
import Navbar from "../components/Navbar"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {

  return (
    <html lang="en">
      <body className="bg-gray-100">

        <AuthProvider>
          <Navbar />
          <div className="p-6">
            {children}
          </div>
        </AuthProvider>

      </body>
    </html>
  )
}