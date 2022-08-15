import { Card } from '@yearn-finance/web-lib/components'
import { ReactElement } from 'react'

function Content(): ReactElement {
  return (
    <div className={'w-full'}>
      <div className={'flex w-full flex-col gap-2'}>
        <h4 className={'mb-2'}>{'Efficient Frontier'}</h4>
        <div className={'mb-6 space-y-2'}>
          <iframe
            src='https://datapane.com/reports/W3DrWPk/defi-frontier/embed/'
            className={'w-full h-screen border-none'}
          >
            IFrame not supported
          </iframe>
        </div>
      </div>
    </div>
  )
}

function Index(): ReactElement {
  return (
    <section aria-label={'some default section'}>
      <Card>
        <Content />
      </Card>
    </section>
  )
}

export default Index
