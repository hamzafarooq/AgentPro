import { IncomingForm } from 'formidable';
import fs from 'fs';
import path from 'path';
import db from '../../utils/db';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async (req, res) => {
  const form = new IncomingForm();
  form.parse(req, async (err, fields, files) => {
    if (err) {
      return res.status(500).json({ error: 'Error parsing form data' });
    }

    const { id, title, author, keyword, content, date } = fields;
    const image = files.image;

    let userpic;
    if (image) {
      const validExtensions = ['jpeg', 'jpg', 'bmp', 'png', 'gif'];
      const ext = path.extname(image.name).toLowerCase().replace('.', '');
      userpic = `img_${Math.floor(Math.random() * 1000000)}.${ext}`;

      if (validExtensions.includes(ext)) {
        const oldPath = image.path;
        const newPath = path.join(process.cwd(), 'public', 'image', userpic);

        fs.rename(oldPath, newPath, async (err) => {
          if (err) {
            return res.status(500).json({ error: 'Error saving image' });
          }

          const query = 'UPDATE posts SET title = ?, author = ?, keyword = ?, image = ?, content = ?, date = ? WHERE id = ?';
          const values = [title, author, keyword, userpic, content, date, id];

          try {
            await db.query(query, values);
            res.status(200).json({ message: 'Post updated successfully' });
          } catch (error) {
            res.status(500).json({ error: 'Error updating post' });
          }
        });
      } else {
        res.status(400).json({ error: 'Invalid image extension' });
      }
    } else {
      const query = 'UPDATE posts SET title = ?, author = ?, keyword = ?, content = ?, date = ? WHERE id = ?';
      const values = [title, author, keyword, content, date, id];

      try {
        await db.query(query, values);
        res.status(200).json({ message: 'Post updated successfully' });
      } catch (error) {
        res.status(500).json({ error: 'Error updating post' });
      }
    }
  });
};