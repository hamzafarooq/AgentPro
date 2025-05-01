import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Edit() {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [email, setEmail] = useState('');
  const router = useRouter();
  const { id } = router.query;

  useEffect(() => {
    if (id) {
      fetch(`/api/user?id=${id}`)
        .then((res) => res.json())
        .then((data) => {
          setName(data.name);
          setAge(data.age);
          setEmail(data.email);
        });
    }
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch('/api/edit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id, name, age, email }),
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
      <h2>Edit Data</h2>
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
        <button type="submit">Update</button>
      </form>
    </div>
  );
}