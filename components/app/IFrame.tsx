import { useState, useEffect } from "react";

interface IProps {
  src: string;
}

export const IFrame: React.FC<IProps> = ({ src }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  return isMounted ? (
    <iframe src={src} className={"w-full h-screen border-none"}>
      IFrame not supported
    </iframe>
  ) : null;
};
