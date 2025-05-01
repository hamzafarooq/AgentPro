import { query } from '../../lib/db';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { id, name, age, email } = req.body;

    if (!name || !age || !email) {
      return res.status(400).json({ error: 'All fields are required' });
    }

    try {
      await query('UPDATE users SET name = ?, age = ?, email = ? WHERE id = ?', [name, age, email, id]);
      res.status(200).json({ message: 'Data updated successfully' });
    } catch (error) {
      res.status(500).json({ error: 'Failed to update data' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}