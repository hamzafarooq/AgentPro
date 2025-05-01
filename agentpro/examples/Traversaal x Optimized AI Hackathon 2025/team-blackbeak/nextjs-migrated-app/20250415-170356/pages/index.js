import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/api/users')
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  const handleDelete = async (id) => {
    const res = await fetch(`/api/delete?id=${id}`, {
      method: 'DELETE',
    });

    if (res.ok) {
      setData(data.filter((item) => item.id !== id));
    } else {
      const data = await res.json();
      alert(data.error);
    }
  };

  return (
    <div>
      <h2>Homepage</h2>
      <Link href="/add">Add New Data</Link>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Email</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{item.age}</td>
              <td>{item.email}</td>
              <td>
                <Link href={`/edit?id=${item.id}`}>Edit</Link> |
                <button onClick={() => handleDelete(item.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}