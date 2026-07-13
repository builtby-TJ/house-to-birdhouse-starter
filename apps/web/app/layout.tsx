import type { ReactNode } from "react";
import "./styles.css";

export const metadata = {
  title: "House to Birdhouse",
  description: "Create a six-part 3D-printable birdhouse from house photographs."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
