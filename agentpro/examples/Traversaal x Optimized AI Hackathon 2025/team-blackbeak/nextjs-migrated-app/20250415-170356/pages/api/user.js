import { query } from '../../lib/db';

export default async function handler(req, res) {
  if (req.method === 'GET') {
    const { id } = req.query;

    try {
      const [user] = await query('SELECT * FROM users WHERE id = ?', [id]);
      res.status(200).json(user);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch user data' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}