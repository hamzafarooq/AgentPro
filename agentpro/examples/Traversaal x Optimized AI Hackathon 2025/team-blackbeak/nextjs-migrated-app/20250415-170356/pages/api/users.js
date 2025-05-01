import { query } from '../../lib/db';

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const users = await query('SELECT * FROM users ORDER BY id DESC');
      res.status(200).json(users);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch users' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}