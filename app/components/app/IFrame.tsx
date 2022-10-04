import {useState, useEffect} from 'react';

type IProps = {
  src: string;
}

export const IFrame: React.FC<IProps> = ({src}) => {
	const [isMounted, setIsMounted] = useState(false);

	useEffect(() => {
		setIsMounted(true);
	}, []);

	return isMounted ? (
		<iframe src={src} className={'h-screen w-full border-none'}>
			{'IFrame not supported'}
		</iframe>
	) : null;
};
