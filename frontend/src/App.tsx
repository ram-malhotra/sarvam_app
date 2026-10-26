import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import CustomerPage from './pages/CustomerPage';
import KitchenDashboard from './pages/KitchenDashboard';
import QRGenerator from './pages/QRGenerator';
import LandingPage from './pages/LandingPage';

export function App() {
  return (
    <Router>
      <Routes>
        {/* Customer Voice Menu & Order Route */}
        <Route path="/r/:restaurantId/:tableId" element={<CustomerPage />} />

        {/* Kitchen Dashboard Route */}
        <Route path="/kitchen/:restaurantId" element={<KitchenDashboard />} />

        {/* Kitchen QR Code Generator Route */}
        <Route path="/kitchen/:restaurantId/qr" element={<QRGenerator />} />

        {/* Landing & Demo Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
