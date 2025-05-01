import db from '../../utils/db';
import fs from 'fs';
import path from 'path';

export default async (req, res) => {
  const { id } = req.query;

  const query = 'SELECT image FROM posts WHERE id = ?';
  const values = [id];

  try {
    const [rows] = await db.query(query, values);
    const imagePath = path.join(process.cwd(), 'public', 'image', rows[0].image);

    fs.unlink(imagePath, async (err) => {
      if (err) {
        return res.status(500).json({ error: 'Error deleting image' });
      }

      const deleteQuery = 'DELETE FROM posts WHERE id = ?';
      await db.query(deleteQuery, values);
      res.status(200).json({ message: 'Post deleted successfully' });
    });
  } catch (error) {
    res.status(500).json({ error: 'Error deleting post' });
  }
};