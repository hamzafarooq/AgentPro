import { query } from '../../lib/db';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { name, age, email } = req.body;

    if (!name || !age || !email) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    try {
      await query('INSERT INTO users (name, age, email) VALUES (?, ?, ?)', [name, age, email]);
      res.status(200).json({ message: 'Data added successfully' });
    } catch (error) {
      res.status(500).json({ error: 'Failed to add data' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}