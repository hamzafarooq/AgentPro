import { useEffect } from 'react';
import { useRouter } from 'next/router';

const DeleteUsers = () => {
  const router = useRouter();
  const { id } = router.query;

  useEffect(() => {
    const deleteUser = async () => {
      const res = await fetch(`/api/deleteusers?id=${id}`, {
        method: 'DELETE',
      });

      if (res.ok) {
        router.push('/viewusers');
      }
    };

    deleteUser();
  }, [id, router]);

  return null;
};

export default DeleteUsers;