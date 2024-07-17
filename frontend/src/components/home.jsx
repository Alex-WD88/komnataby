import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Home = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      // Если токена нет, перенаправляем на страницу входа
      window.location.href = '/login';
    } else {
      (async () => {
        try {
          const config = {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}` // Важно использовать Bearer токен
            },
            withCredentials: true,
          };
          // Добавляем токен авторизации в заголовки запроса
          const {data} = await axios.get(
            'http://localhost:8000/home/',
            config
          );
          setMessage(data.message);
        } catch (error) {
          console.log('not auth');
        }
      })();
    }
  }, []);

  return (
    <>
      <div className="form-signin mt-5 text-center">
        <h3>Hi {message}</h3>
      </div>
    </>
  );
}

export default Home;