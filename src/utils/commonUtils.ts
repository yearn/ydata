
export const toArray = (arrayLike: any): any[] => {
  if (Array.isArray(arrayLike)) {
    return arrayLike;
  } else {
    return [arrayLike];
  }
}