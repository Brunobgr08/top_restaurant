import { useState, FormEvent } from 'react';
import './styles.css';

function App() {
  const [name, setName] = useState<string>('');
  const [menu, setMenu] = useState<string>('Burger');
  const [status, setStatus] = useState<string>('');
  const [showStatus, setShowStatus] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const orderData = {
      customer_name: name,
      item: menu,
    };

    try {
      const response = await fetch('http://order-service:5001/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData),
      });

      const result: ApiResponse = await response.json();

      if (response.ok) {
        setStatus(`Pedido #${result.data?.id} criado com sucesso! Aguarde a notificação.`);
        setShowStatus(true);
        setName('');
        setMenu('Burger');
      } else {
        setStatus(`Erro: ${result.message || 'Erro ao criar pedido.'}`);
        setShowStatus(true);
      }
    } catch (err) {
      setStatus('Erro na comunicação com o servidor.');
      setShowStatus(true);
      console.error('Error:', err);
    }
  };

  return (
    <div className="container">
      <h1>Realizar Pedido</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="menu">Escolha o prato:</label>
        <select id="menu" required value={menu} onChange={(e) => setMenu(e.target.value)}>
          <option value="Burger">Burger - R$ 25</option>
          <option value="Pizza">Pizza - R$ 40</option>
          <option value="Salad">Salada - R$ 20</option>
        </select>

        <div className="name-container">
          <label htmlFor="name">Seu nome:</label>
          <input
            type="text"
            id="name"
            required
            placeholder="Digite seu nome"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <button type="submit">Enviar Pedido</button>
      </form>

      {showStatus && <div className="status">{status}</div>}
    </div>
  );
}

export default App;
