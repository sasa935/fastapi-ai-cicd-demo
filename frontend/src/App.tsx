import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Links } from "./pages/Links";
import { Stats } from "./pages/Stats";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="links" element={<Links />} />
        <Route path="links/:id" element={<Stats />} />
      </Route>
    </Routes>
  );
}
