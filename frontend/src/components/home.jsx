import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Home = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
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
  }, []);

  return (
    <>
      <div className="form-signin mt-5 text-center">
        {message ? <h3>Hi {message}</h3> : null}
      </div>
    </>
  );
}

export default Home;