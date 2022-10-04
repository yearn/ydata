import React, {useState, useEffect, ReactElement} from 'react';

type TProps = {
  src: string;
}

export const IFrame: React.FC<TProps> = ({src}): ReactElement | null => {
	const [isMounted, set_isMounted] = useState(false);

	useEffect((): void => {
		set_isMounted(true);
	}, []);

	return isMounted ? (
		<iframe src={src} className={'h-screen w-full border-none'}>
			{'IFrame not supported'}
		</iframe>
	) : null;
};
