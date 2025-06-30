import { useState } from 'react';
import { fetchMenu } from '../services/api';
import { MenuItem } from '../services/types';

export function useMenu() {
  const [menu, setMenu] = useState<MenuItem[]>([]);

  const fetchMenuItems = async () => {
    const result = await fetchMenu();
    setMenu(result);
  };

  return { menu, fetchMenu: fetchMenuItems };
}