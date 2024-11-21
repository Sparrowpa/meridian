import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Box } from "@mui/material";

function App() {
  const [metrics, setMetrics] = useState(null);
  const [closedTrades, setClosedTrades] = useState([]);

  useEffect(() => {
    // Загружаем данные с API
    axios
      .get("http://localhost:5000/api/get_test_data")  // URL к вашему Flask серверу
      .then((response) => {
        const data = response.data[0]; // Получаем данные из первого элемента массива
        setMetrics(data.metrics);
        setClosedTrades(data.closed_trades);
      })
      .catch((error) => {
        console.error("Ошибка при загрузке данных:", error);
      });
  }, []);

  // Функция для форматирования даты без изменения часового пояса
  const formatDate = (dateString) => {
    const date = new Date(dateString); // Создаем объект даты из строки
    const day = String(date.getUTCDate()).padStart(2, '0'); // День с ведущим нулем
    const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // Месяц с ведущим нулем
    const year = date.getUTCFullYear();
    const hours = String(date.getUTCHours()).padStart(2, '0'); // Часы с ведущим нулем
    const minutes = String(date.getUTCMinutes()).padStart(2, '0'); // Минуты с ведущим нулем
    const seconds = String(date.getUTCSeconds()).padStart(2, '0'); // Секунды с ведущим нулем
    return `${day}.${month}.${year}, ${hours}:${minutes}:${seconds}`;
  };

  return (
    <Box sx={{ padding: 2 }}>
      {/* Метрики */}
      <Typography variant="h5" gutterBottom>
        Метрики
      </Typography>
      {metrics ? (
        <TableContainer component={Paper} sx={{ marginBottom: 4 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Profit Factor</TableCell>
                <TableCell>Return</TableCell>
                <TableCell>Return %</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>{metrics.profit_factor}</TableCell>
                <TableCell>{metrics.return}</TableCell>
                <TableCell>{metrics.return_percent}%</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body1" color="error">Метрики недоступны</Typography>
      )}

      {/* Закрытые сделки */}
      <Typography variant="h5" gutterBottom>
        Закрытые сделки
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Trade ID</TableCell>
              <TableCell>Open Time</TableCell>
              <TableCell>Close Time</TableCell>
              <TableCell>Open Price</TableCell>
              <TableCell>Close Price</TableCell>
              <TableCell>Profit/Loss</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {closedTrades
              .sort((a, b) => new Date(a.open_time) - new Date(b.open_time)) // Сортируем по времени открытия сделки
              .map((trade) => (
                <TableRow key={trade.id}>
                  <TableCell>{trade.id}</TableCell>
                  <TableCell>{formatDate(trade.open_time)}</TableCell> {/* Форматируем время */}
                  <TableCell>{formatDate(trade.close_time)}</TableCell> {/* Форматируем время */}
                  <TableCell>{trade.open_price}</TableCell>
                  <TableCell>{trade.close_price}</TableCell>
                  <TableCell
                    style={{
                      color: trade.profit_loss >= 0 ? "green" : "red",
                    }}
                  >
                    {trade.profit_loss}
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default App;
