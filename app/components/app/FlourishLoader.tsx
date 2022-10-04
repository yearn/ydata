import {useState, useEffect} from 'react';

type IProps = {
  src: string;
}

export const FlourishLoader: React.FC<IProps> = ({src}) => {
	const [isMounted, setIsMounted] = useState(false);

	useEffect(() => {
		setIsMounted(true);
	}, []);

	return isMounted ? (
		<iframe
			src={`https://flo.uri.sh/${src}/embed`}
			className={'flourish-embed-iframe h-screen w-full border-none'}
			sandbox={'allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'}
		/>
	) : null;
};
