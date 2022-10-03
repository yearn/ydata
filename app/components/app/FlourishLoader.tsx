import { useState, useEffect } from "react";

interface IProps {
  src: string;
}

export const FlourishLoader: React.FC<IProps> = ({ src }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  return isMounted ? (
    <iframe
      src={`https://flo.uri.sh/${src}/embed`}
      className="flourish-embed-iframe w-full h-screen border-none"
      sandbox="allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation"
    />
  ) : null;
};
