import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Add() {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [email, setEmail] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch('/api/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, age, email }),
    });

    if (res.ok) {
      router.push('/');
    } else {
      const data = await res.json();
      alert(data.error);
    }
  };

  return (
    <div>
      <h2>Add Data</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label>Age:</label>
          <input type="text" value={age} onChange={(e) => setAge(e.target.value)} />
        </div>
        <div>
          <label>Email:</label>
          <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <button type="submit">Add</button>
      </form>
    </div>
  );
}