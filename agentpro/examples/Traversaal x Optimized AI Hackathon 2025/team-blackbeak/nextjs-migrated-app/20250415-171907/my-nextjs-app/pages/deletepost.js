import { useEffect } from 'react';
import { useRouter } from 'next/router';

const DeletePost = () => {
  const router = useRouter();
  const { id } = router.query;

  useEffect(() => {
    const deletePost = async () => {
      const res = await fetch(`/api/deletepost?id=${id}`, {
        method: 'DELETE',
      });

      if (res.ok) {
        router.push('/viewpost');
      }
    };

    deletePost();
  }, [id, router]);

  return null;
};

export default DeletePost;