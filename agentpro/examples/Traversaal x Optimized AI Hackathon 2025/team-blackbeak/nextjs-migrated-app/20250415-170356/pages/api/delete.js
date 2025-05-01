import { query } from '../../lib/db';

export default async function handler(req, res) {
  if (req.method === 'DELETE') {
    const { id } = req.query;

    try {
      await query('DELETE FROM users WHERE id = ?', [id]);
      res.status(200).json({ message: 'Data deleted successfully' });
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete data' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}