import Navbar from "./Navbar";
import { useLocation } from "react-router-dom";

export default function Layout({ children }) {
  const location = useLocation();
  
  // Rotas que não mostram navbar (login e superuser login)
  const hideNavbarRoutes = ["/", "/login", "/superuser"];
  const showNavbar = !hideNavbarRoutes.includes(location.pathname);

  return (
    <>
      {showNavbar && <Navbar />}
      <main>
        {children}
      </main>
    </>
  );
}
