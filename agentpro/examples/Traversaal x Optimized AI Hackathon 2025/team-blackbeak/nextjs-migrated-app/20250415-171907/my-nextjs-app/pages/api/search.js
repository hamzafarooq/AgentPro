import db from '../../utils/db';

export default async (req, res) => {
  const { search } = req.query;

  const query = 'SELECT * FROM posts WHERE author LIKE ? OR title LIKE ?';
  const values = [`%${search}%`, `%${search}%`];

  try {
    const [rows] = await db.query(query, values);
    res.status(200).json(rows);
  } catch (error) {
    res.status(500).json({ error: 'Error searching posts' });
  }
};