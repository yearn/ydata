import React, {useState, useEffect, ReactElement} from 'react';

type TProps = {
  src: string;
}

export const FlourishLoader: React.FC<TProps> = ({src}): ReactElement | null => {
	const [isMounted, set_isMounted] = useState(false);

	useEffect((): void => {
		set_isMounted(true);
	}, []);

	return isMounted ? (
		<iframe
			src={`https://flo.uri.sh/${src}/embed`}
			className={'flourish-embed-iframe mt-5 h-5/6 w-full border-none'}
			sandbox={'allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation'}
		/>
	) : null;
};
